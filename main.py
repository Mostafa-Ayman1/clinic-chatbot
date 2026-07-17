import openai
import gradio as gr 
import agents
from config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL
from prompts import ROUTER_PROMPT

client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

def router(user_message, history):
    try:
        # ========================
        # Context-Aware Router
        # ========================
        router_messages = [{"role": "system", "content": ROUTER_PROMPT}]

 
        last_bot_response = None
        if history and len(history) > 0:
            for turn in reversed(history):
                if isinstance(turn, dict) and turn.get("role") == "assistant" and turn.get("content"):
                    last_bot_response = turn["content"]
                    break
        

        if last_bot_response:
            router_messages.append({
                "role": "assistant",
                "content": f"السياق: أنا سألت المريض في الرسالة السابقة قائلاً: {last_bot_response}"
            })

       
        router_messages.append({"role": "user", "content": f"رسالة المريض الحالية: {user_message}"})

        print(f"🧠 Context sent to router: {last_bot_response!r}")

        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=router_messages
        )

        intent = response.choices[0].message.content.strip().upper()
        print(f"🎯 Intent Detected: {intent}")

        if intent == "FAQ":
            print("🚀 Routing to FAQ Agent...")
            return agents.handle_faq(user_message)

        elif intent == "BOOKING":
            print("🚀 Routing to Booking Agent...")
            return agents.handle_booking(user_message, history)

        elif intent == "MEDICAL_QUESTION":
            print("🚨 Medical Question Detected. Routing to Medical Disclaimer...")
            return """
                    عذراً، أنا المساعد الآلي المخصص للحجوزات والاستفسارات الإدارية فقط.
                    للحفاظ على سلامتك، لا يمكنني تقديم أي استشارات طبية أو تشخيص للأعراض. 
                    يرجى حجز موعد ليتمكن الطبيب من تقييم حالتك بشكل صحيح، أو سيتم تحويلك الآن للتحدث مع السكرتارية.
                    """

        elif intent == "GREETING":
            return "مرحباً بك في عيادتنا! 👋\nكيف يمكنني مساعدتك اليوم؟ (استفسار عن المواعيد، الأسعار)"

        else:
            return "مرحباً! كيف يمكنني مساعدتك اليوم؟ (مواعيد، أسعار)"

    except Exception as e:
        print(f"Error: {e}")
        return "عذراً، أواجه مشكلة تقنية حالياً. يرجى المحاولة بعد قليل. ⚙️"

# ==========================================
# (Gradio ChatInterface)
# ==========================================

chatbot = gr.ChatInterface(
    fn=router,
    title=" العيادة الذكية - المساعد الآلي",
    description="أهلاً بك! أنا المساعد الذكي للعيادة، جاهز للرد على استفساراتك أو مساعدتك في حجز موعد.",

    chatbot=gr.Chatbot(
        avatar_images=(
            "https://ui-avatars.com/api/?name=User&background=random",
            "https://ui-avatars.com/api/?name=Bot&background=0D8ABC&color=fff"
        )
    ),

    
    textbox=gr.Textbox(
        placeholder="اكتب استفسارك هنا (مثال: بكام الكشف؟) ...",
        container=False,
        scale=7
    ),


    examples=[
        "العنوان بتاعكم فين؟",
        "بكام الكشف؟ ومواعيدكم إمتى؟",
        "هل عندكم دكتور أسنان؟",
        "ممكن أعرف أسعار التحاليل؟"
    ],
)

if __name__ == "__main__":
    chatbot.launch()
