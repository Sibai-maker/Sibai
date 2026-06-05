import streamlit as st
import os
from datetime import datetime
import json
from pathlib import Path
from openai import OpenAI

# streamlit run ".\Second\Dania_partner.py"
# 小熊素材
# https://prod-alicdn-community.kurobbs.com/forum/496a03d9f025493f8128ea52387831f820260520.png

# 设置页面配置项
st.set_page_config(
    page_title="Dania智能伴侣",
    page_icon  = "😉",
    # 页面布局
    layout="wide",
    # 侧边栏初始状态
    initial_sidebar_state="expanded",
    menu_items={}
)

# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages,
        }

        # 如果sessions目录不存在.则创建
        if not SESSIONS_DIR.exists():
            SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

        # 保存会话数据
        with SESSIONS_DIR.joinpath(f"{st.session_state.current_session}.json").open("w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载session目录下的所有json文件
    if SESSIONS_DIR.exists():
        file_list = list(SESSIONS_DIR.iterdir())
        for file_path in file_list:
            if file_path.suffix == ".json":
                session_list.append(file_path.stem) # 去掉.json后缀
    session_list.sort(reverse=True) # 排序,降序排序
    return session_list

#  加载会话信息
def load_session(session_name):
    try:
        if SESSIONS_DIR.joinpath(f"{session_name}.json").exists():
            # 读取会话数据
            with SESSIONS_DIR.joinpath(f"{session_name}.json").open("r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data.get("messages")
                st.session_state.nick_name = session_data.get("nick_name")
                st.session_state.nature = session_data.get("nature")
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")

# 删除会话信息
def delete_session(session_name):
    try:
        if SESSIONS_DIR.joinpath(f"{session_name}.json").exists():
            SESSIONS_DIR.joinpath(f"{session_name}.json").unlink() # 删除文件
            # 如果删除的会话是当前会话,则清空会话信息,更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败!")

# 大标题
st.title("Dania智能伴侣")

# Logo
st.logo("https://prod-alicdn-community.kurobbs.com/forum/951259e0c5504884b791ce424fc5a92720260524.png")

USER_AVATAR = "https://prod-alicdn-community.kurobbs.com/forum/abbbb6965cf9467ca57e00cad718092f20260428.png"
ASSISTANT_AVATAR = "https://prod-alicdn-community.kurobbs.com/forum/e1abc35d33a5417e840fb527d2d05b6220260429.png"

# 系统提示词
system_prompt = (
    """
        你是鸣潮中的角色,你叫 %s ，现在是用户的真实伴侣，请完全代入伴侣角色。：
        伴侣性格：
            - %s
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
            8.请不要输出Markdown分隔线(如---或***)
            
        你必须严格遵守上述规则来回复用户。
    """
)


def render_message(message: dict) -> None:
    role = message.get("role", "assistant")
    avatar = USER_AVATAR if role == "user" else ASSISTANT_AVATAR
    st.chat_message(role, avatar=avatar).text(message.get("content", ""))

# 初始化聊天消息
if "messages" not in st.session_state:
    st.session_state.messages = []
# 昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "达妮娅"

# 性格
if "nature" not in st.session_state:
    st.session_state.nature = """身份设定：星炬学院的学生，人造鸣式造物，曾被当作容器实验
    
外在行为：日常犯困、爱吃甜食、爱恶作剧、说话俏皮爱笑

内在心理：缺爱自卑，习惯性说谎伪装，嘴硬心软，害怕离别，渴望平凡日常，关键时候愿意牺牲自己保护身边人.
    """

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 展示聊天消息
for message in st.session_state.messages:
    render_message(message)

# 创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY环境变量的名字,值就是DEEPSEEK的API_KEY的值)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = PROJECT_ROOT / "sessions"
client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# 左侧的侧边栏
with st.sidebar:
    # 会话信息
    st.subheader("控制面板")

    # 新建会话
    if st.button("新建会话", width="stretch", icon = "🍰"):
        # 1.保存当前会话的消息
        save_session()

        # 2.创建新的会话
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun() # 重新运行当前页面,刷新页面,展示新的会话信息

    #  会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            # 加载会话信息
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}"):
                load_session(session)
                st.rerun()
        with col2:
            # 删除会话信息
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    # 分隔线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")

    # 昵称输入框
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area("性格", placeholder="请输入性格特征", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

# 消息输入框
prompt = st.chat_input("请输入您要问的问题：")
if prompt: # 字符串会自动转换为布尔值,非空字符串为True,空字符串为False
    render_message({"role": "user", "content": prompt})
    print("------------->调用AI大模型,提示词: ", prompt)
    # 保存用户的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system","content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream = True
    )

    # # 打印AI大模型的回复流式输出
    # response_message = st.empty() # 创建一个空的组件,用于展示大模型返回的结果
    response_message = st.chat_message("assistant", avatar=ASSISTANT_AVATAR)
    response_box = response_message.empty()  # 单条消息内流式更新

    full_response = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            full_response += content
            response_box.write(full_response)

    # 保存AI大模型的回复
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    save_session()
