import json
import requests
from openai import OpenAI
from prompts import HANDLE_FAQ_PROMPT, HANDLE_BOOKING_PROMPT
from config import OPENAI_API_KEY, N8N_WEBHOOK, OPENAI_MODEL, OPENAI_API_BASE


client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
FAQ_WEBHOOK = N8N_WEBHOOK


ALLOWED_KEYWORDS_LIST = [
    "مواعيد", "دوام", "ساعات العمل", "عنوان", "موقع", "مكان", "حجز", "موعد",
    "تغيير", "تعديل", "إلغاء", "حذف", "تخصص", "دكتور", "طبيب", "سعر", "كشف",
    "تكلفة", "دفع", "فيزا", "كاش", "تأمين", "شركة تأمين", "تحاليل", "معمل",
    "أشعة", "X-Ray", "صيدلية", "دواء", "نتيجة", "تقرير", "ملف طبي", "هاتف",
    "رقم", "اتصال", "واتساب", "WhatsApp", "باركينج", "سيارات", "طوارئ",
    "إسعاف", "حضور", "تسجيلي",
]
ALLOWED_KEYWORDS = "، ".join(ALLOWED_KEYWORDS_LIST)

# ---------------------------------------------------------
# 2. Tools for FAQ and Booking Agents
# ---------------------------------------------------------

faq_tools = [
    {
        "type": "function",
        "function": {
            "name": "send_keywords_to_n8n",
            "description": "يستخدم للبحث عن معلومات العيادة بإرسال الكلمات المفتاحية إلى قاعدة البيانات.",
            "parameters": {
                "type": "object",
                "properties": {
                    "extracted_keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": f"استخرج الكلمات المفتاحية من رسالة المريض. يجب أن تكون الكلمات من هذه القائمة فقط: {ALLOWED_KEYWORDS}"
                    }
                },
                "required": ["extracted_keywords"]
            }
        }
    }
]
booking_tools = [
    {
        "type": "function",
        "function": {
            "name": "submit_booking",
            "description": "يستخدم لإرسال بيانات الحجز المكتملة إلى قاعدة البيانات لتأكيد الموعد.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "specialty": {"type": "string"},
                    "preferred_time": {"type": "string"}
                },
                "required": ["patient_name", "phone_number", "specialty", "preferred_time"]
            }
        }
    }
]


def _filter_allowed_keywords(keywords_list):
    """
   Use server-side validation to check that the words extracted by the model are really in the allowed list,
   instead of only trusting the model to follow the rules.
    """
    allowed_set = {kw.strip().lower() for kw in ALLOWED_KEYWORDS_LIST}
    filtered = [kw for kw in keywords_list if kw.strip().lower() in allowed_set]

    dropped = set(keywords_list) - set(filtered)
    if dropped:
        print(f"⚠️ Dropped out-of-list keywords: {dropped}")

    return filtered


def handle_faq(user_message):

    messages = [
        {"role": "system", "content": HANDLE_FAQ_PROMPT},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        tools=faq_tools,
        tool_choice="auto",
        temperature=0.2
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        tool_call = tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        raw_keywords = arguments.get("extracted_keywords", [])

        keywords_list = _filter_allowed_keywords(raw_keywords)

        print(f"🔍 AI Extracted Keywords: {keywords_list}")

        payload = {
            "action": "search_faq",
            "keywords": keywords_list
        }

        try:
            webhook_response = requests.post(FAQ_WEBHOOK, json=payload, timeout=10)
            webhook_response.raise_for_status()
            n8n_data = webhook_response.json()
        except requests.exceptions.RequestException as e:
            print(f"🚨 n8n Webhook Error: {e}")
            n8n_data = "تعذر الاتصال بقاعدة البيانات حالياً."
        except ValueError as e:
            # خطأ في تحويل الرد إلى JSON
            print(f"🚨 n8n Response Parsing Error: {e}")
            n8n_data = "تعذر قراءة رد قاعدة البيانات حالياً."

        messages.append(response_message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": str(n8n_data)
        })

        final_response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2
        )

        return final_response.choices[0].message.content or "عذراً، لم أتمكن من إيجاد رد مناسب، برجاء إعادة صياغة سؤالك."

    return response_message.content or "عذراً، لم أفهم طلبك، ممكن توضحه أكتر؟"


def handle_booking(user_message, chat_history):
    messages = [{"role": "system", "content": HANDLE_BOOKING_PROMPT}]
   
    if chat_history:
        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
            
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        tools=booking_tools,
        tool_choice="auto",
        temperature=0.2
    )
    print("🤖 Test Response AI")
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        tool_call = tool_calls[0]
        booking_data = json.loads(tool_call.function.arguments)
        booking_data = { "action": "submit_booking", **booking_data }  
        print(f"✅ Data Ready for n8n: {booking_data}")
        try:
            webhook_response = requests.post(N8N_WEBHOOK, json=booking_data, timeout=10)
            webhook_response.raise_for_status()

            patient_name = booking_data.get("patient_name", "عزيزي المريض")
            return f"تم تأكيد طلب الحجز بنجاح يا {patient_name}! سنتواصل معك قريباً على رقمك."

        except requests.exceptions.RequestException as e:
            print(f"🚨 Booking Webhook Error: {e}")
            return "عذراً، حدث خطأ أثناء تسجيل الحجز. يرجى المحاولة لاحقاً."
        except KeyError as e:
            print(f"🚨 Missing booking field: {e}")
            return "عذراً، بيانات الحجز غير مكتملة. برجاء إرسالها مرة أخرى."

    return response_message.content or "ممكن تأكدلي بيانات الحجز (الاسم، الرقم، التخصص، والموعد المفضل)؟"