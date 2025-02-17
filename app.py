import streamlit as st
from openai import OpenAI
from serpapi import GoogleSearch

# Track chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]

# API keys
deepseek_api_key = st.secrets["deepseek_api_key"]
serpapi_api_key = st.secrets["serpapi_api_key"]

def deepseek_chat(api_key: str, messages: list) -> str:
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "You are a helpful assistant"}, *messages],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
        return ""

def search_web(query: str) -> str:
    try:
        params = {
            "q": query,
            "api_key": serpapi_api_key,
            "engine": "google",
            "num": 3  # Número de resultados a serem retornados
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extrair os primeiros resultados
        if "organic_results" in results:
            response = "Here are some results from the web:\n\n"
            for idx, result in enumerate(results["organic_results"][:3], start=1):
                response += f"{idx}. [{result['title']}]({result['link']})\n"
                response += f"   {result['snippet']}\n\n"
            return response
        else:
            return "No results found."
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return ""

def main():
    st.title('🤖 DeepSeek Chatbot')
    
    # Sidebar with user guide
    with st.sidebar:
        st.header("📚 User Guide")
        st.markdown("...") # Add your guide text here
        
        if st.button("Reset Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Verifica se o usuário quer uma busca na web
                if "search for" in prompt.lower() or "find" in prompt.lower():
                    query = prompt.lower().replace("search for", "").replace("find", "").strip()
                    response = search_web(query)
                else:
                    response = deepseek_chat(deepseek_api_key, st.session_state.messages)
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()