import streamlit as st
import re


bot_msg_container_html_template = '''
<div style='background-color: #5e646e; padding: 16px; border-radius: 16px; margin-bottom: 16px; display: flex'>
    <div style="width: 16%; display: flex; justify-content: center">
        <img src="https://st3.depositphotos.com/30456762/37578/v/600/depositphotos_375780486-stock-illustration-chat-bot-robot-avatar-in.jpg" style="max-height: 40px; max-width: 40px; border-radius: 40%;">
    </div>
    <div style="width: 80%; padding-left: 16px;">
        $MSG
    </div>
</div>
'''

user_msg_container_html_template = '''
<div style='background-color: #40444b; padding: 16px; padding-right: 16px; border-radius: 16px; margin-bottom: 16px; display: flex'>
    <div style="width: 80%; padding-left: 16px;">
        $MSG
    </div>
    <div style="width: 16%; margin-left: auto; display: flex; justify-content: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/5965/5965556.png" style="max-width: 40px; max-height: 40px; float: right; border-radius: 40%;">
    </div>    
</div>
'''

def render_article_preview(docs, tickers):
    message = f"<h5>Here are relevant articles for {tickers} that may answer your question. &nbsp; &nbsp;</h5>"
    message += "<div>"
    for d in docs:
        elipse = " ".join(d[2].split(" ")[:140])        
        message += f"<br><a href='{d[1]}'>{d[0]}</a></br>"
        message += f"<p>{elipse} ...</p>"
        message += "<br>"
    message += "</div>"
    return message

def render_earnings_summary(ticker, summary):
    transcript_title = summary["transcript_title"]
    message = f"<h5>Here is summary for {ticker} {transcript_title} </h5>"
    message += "<div>"
    body =  re.sub(r'^-', r'*  ', summary["summary"])
    body =  re.sub(r'\$', r'\\$', body)
    message += f"<p>{body}</p>"
    message += "</div>"
    return message

def render_stock_question(answer, articles):
    message = "<div>"
    message += f"{answer} &nbsp; <br>"
    message += "Sources: "
    for a in articles:
        message += f"<a href='{a[1]}'>{a[0]}</a><br>"
    message += "</div>"
    return message

def render_chat(**kwargs):
    """
    Handles is_user 
    """
    if kwargs["is_user"]:
        st.write(
            user_msg_container_html_template.replace("$MSG", kwargs["message"]),
            unsafe_allow_html=True)
    else:
        st.write(
            bot_msg_container_html_template.replace("$MSG", kwargs["message"]),
            unsafe_allow_html=True)

    if "figs" in kwargs:
        for f in kwargs["figs"]:
            st.plotly_chart(f, use_container_width=True)

