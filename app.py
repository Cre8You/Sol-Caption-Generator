st.title("SOLさん向け キャプション生成ツール")

if st.secrets.get("X_BEARER_TOKEN"):
    st.success("X_BEARER_TOKEN を読み込めています")
else:
    st.error("X_BEARER_TOKEN が見つかりません")
import streamlit as st
from typing import Dict, List

st.set_page_config(page_title="SOLさん向け キャプション生成ツール", page_icon="✍️", layout="wide")

TONES = ["やわらかい", "明るい", "熱量高め", "落ち着いた", "募集向け"]
PLATFORMS = ["X", "Instagram"]
POST_TYPES = ["街ブラ", "写真", "イベント告知", "出演者募集", "リハビリ豆知識"]
CTAS = ["詳細はDMで", "プロフィールのリンクから", "コメント歓迎", "気軽にメッセージください"]
AUDIENCES = ["一般向け", "役者向け", "写真好き向け", "患者向け"]
TREND_REGIONS = ["日本", "東京", "大阪", "福岡"]

SAMPLE_TRENDS: Dict[str, List[Dict[str, str]]] = {
    "日本": [
        {"id": 1, "name": "#桜フォト", "volume": "14.2万件", "angle": "春の景色や街歩き写真と相性◎", "suggestedTheme": "桜の景色と春の街歩き", "suggestedKeywords": "桜, 春, 街歩き, カメラ"},
        {"id": 2, "name": "#週末さんぽ", "volume": "8.6万件", "angle": "街ブラ動画や散歩投稿に自然に混ぜやすい", "suggestedTheme": "週末の街歩きで見つけた風景", "suggestedKeywords": "街歩き, 散歩, 週末, 写真"},
        {"id": 3, "name": "#カフェ巡り", "volume": "11.1万件", "angle": "甘味処やパン屋めぐり系の投稿向け", "suggestedTheme": "街歩きの途中で立ち寄ったカフェ", "suggestedKeywords": "カフェ, パン屋, 街ブラ, 写真"},
    ],
    "東京": [
        {"id": 4, "name": "#上野公園", "volume": "5.3万件", "angle": "季節の景色やおでかけ系に使いやすい", "suggestedTheme": "上野公園で感じた季節の空気", "suggestedKeywords": "上野, 東京, 散歩, 花"},
        {"id": 5, "name": "#谷中銀座", "volume": "3.9万件", "angle": "下町の街ブラ感を出しやすい", "suggestedTheme": "谷中銀座を歩いて見つけた風景", "suggestedKeywords": "谷中銀座, 下町, 街歩き, 写真"},
        {"id": 6, "name": "#東京カメラ部", "volume": "9.8万件", "angle": "写真メインの投稿に寄せやすい", "suggestedTheme": "東京の街で切り取った一枚", "suggestedKeywords": "東京, 写真, カメラ, 街角"},
    ],
    "大阪": [
        {"id": 7, "name": "#中崎町", "volume": "2.7万件", "angle": "街歩きやカフェ系の写真向け", "suggestedTheme": "中崎町で見つけた街の表情", "suggestedKeywords": "中崎町, カフェ, 散歩, 写真"},
        {"id": 8, "name": "#大阪さんぽ", "volume": "4.4万件", "angle": "街ブラ投稿と混ぜやすい定番", "suggestedTheme": "大阪を歩いて見つけた景色", "suggestedKeywords": "大阪, 街歩き, 散歩, カメラ"},
    ],
    "福岡": [
        {"id": 9, "name": "#大濠公園", "volume": "2.1万件", "angle": "自然と街のバランスが取りやすい", "suggestedTheme": "大濠公園で感じたやさしい時間", "suggestedKeywords": "大濠公園, 福岡, 散歩, 写真"},
        {"id": 10, "name": "#福岡カフェ", "volume": "3.6万件", "angle": "カフェ系や街歩きVlog向け", "suggestedTheme": "福岡で立ち寄ったカフェ時間", "suggestedKeywords": "福岡, カフェ, 街歩き, 写真"},
    ],
}


def build_hashtags(post_type: str, platform: str, audience: str, keywords: str) -> List[str]:
    keyword_tags = []
    for part in keywords.replace("、", ",").split(","):
        k = part.strip()
        if k:
            keyword_tags.append(f"#{k.lstrip('#')}")

    base_map = {
        "街ブラ": ["#街ブラ", "#街歩き", "#散歩記録", "#カメラ散歩"],
        "写真": ["#写真", "#写真好き", "#日常を切り取る", "#ファインダー越しの私の世界"],
        "イベント告知": ["#イベント告知", "#開催情報", "#イベント好き", "#参加者募集"],
        "出演者募集": ["#出演者募集", "#キャスト募集", "#朗読劇", "#表現活動"],
        "リハビリ豆知識": ["#リハビリ", "#健康情報", "#身体づくり", "#セルフケア"],
    }
    audience_map = {
        "一般向け": ["#日々の記録", "#今日の一枚"],
        "役者向け": ["#役者", "#舞台好き"],
        "写真好き向け": ["#写真好きな人と繋がりたい", "#カメラ好き"],
        "患者向け": ["#健康習慣", "#無理なく続ける"],
    }
    platform_map = {
        "X": ["#拡散希望"],
        "Instagram": ["#instagood"],
    }

    combined = base_map[post_type] + audience_map[audience] + platform_map[platform] + keyword_tags
    deduped = list(dict.fromkeys(combined))
    return deduped[:10]



def build_caption(
    platform: str,
    post_type: str,
    tone: str,
    theme: str,
    keywords: str,
    cta: str,
    location: str,
    deadline: str,
    notes: str,
    emoji: bool,
    line_breaks: bool,
) -> str:
    def icon(value: str) -> str:
        return value if emoji else ""

    sparkle = icon("✨")
    megaphone = icon("📣")
    camera = icon("📸")
    pin = icon("📍")
    clock = icon("⏰")
    heart = icon("💫")
    wave = icon("🫶")
    leaf = icon("🍃")
    coffee = icon("☕")
    shoes = icon("👟")
    sun = icon("☀️")
    star = icon("🌟")

    keyword_list = [v.strip() for v in keywords.replace("、", ",").split(",") if v.strip()]
    keyword_text = "、".join(keyword_list)

    if keyword_text:
        if platform == "X":
            keyword_sentence = f"今日は{keyword_text}をテーマに、空気ごと届けてみます{sparkle}"
        else:
            keyword_sentence = f"{keyword_text}を感じた時間を、ことばでもそっと残してみます{sparkle}"
    else:
        keyword_sentence = ""

    note_lines = []
    raw_lines = [line.strip() for line in notes.splitlines() if line.strip()]
    icons = [heart, sparkle, leaf, star]
    for idx, line in enumerate(raw_lines):
        if emoji and any(icons):
            usable_icons = [i for i in icons if i]
            prefix = usable_icons[idx % len(usable_icons)] if usable_icons else ""
            note_lines.append(f"{prefix} {line}".strip())
        else:
            note_lines.append(line)

    if post_type == "街ブラ":
        intro = f"いつもの街を歩いていたら、{theme}にふっと出会えました{shoes}" if platform == "X" else f"いつもの街をゆっくり歩いていたら、{theme}に出会えた日{shoes}"
    elif post_type == "写真":
        intro = f"{theme}を切り取った一枚です。眺めていた空気まで写っていた気がします{camera}{sparkle}" if platform == "X" else f"{theme}を切り取った一枚です。見返すたび、そのときの空気まで思い出します{camera}{sparkle}"
    elif post_type == "イベント告知":
        intro = f"{theme}のお知らせです。気になっていた方に届いたらうれしいです{megaphone}{star}" if platform == "X" else f"{theme}のお知らせです。参加を考えている方に、やさしく届きますように{megaphone}{star}"
    elif post_type == "出演者募集":
        intro = f"{theme}の参加者を募集しています。表現が好きな方に届いたらうれしいです{megaphone}{heart}" if platform == "X" else f"{theme}の参加者を募集しています。ことばや表現が好きな方と出会えたらうれしいです{megaphone}{heart}"
    else:
        intro = f"{theme}について、毎日の中で取り入れやすい形でまとめてみました{leaf}{sparkle}" if platform == "X" else f"{theme}について、毎日の中で無理なく取り入れやすい形でまとめました{leaf}{sparkle}"

    if location:
        location_sentence = f"{pin} 場所は{location}。歩いているだけで気持ちがほどけるような空気でした{sun}" if platform == "X" else f"{pin} 場所は{location}。景色だけじゃなく、その場の温度まで残しておきたくなりました{sun}"
    else:
        location_sentence = ""

    if deadline:
        deadline_sentence = f"{clock} 締切は{deadline}です。気になる方はどうぞお早めに{sparkle}" if platform == "X" else f"{clock} 応募や参加の締切は{deadline}です。タイミングが合う方はぜひチェックしてみてください{sparkle}"
    else:
        deadline_sentence = ""

    tone_ending_map = {
        "やわらかい": f"やさしい余韻まで届いたらうれしいです{heart}",
        "明るい": f"楽しい気配まで一緒に届きますように{sparkle}",
        "熱量高め": f"気持ちごとまっすぐ届いたらうれしいです{megaphone}",
        "落ち着いた": f"静かな温度感で受け取ってもらえたらうれしいです{leaf}",
        "募集向け": f"一歩踏み出すきっかけになれたらうれしいです{wave}",
    }

    extras = []
    if post_type == "街ブラ" and emoji:
        extras.append(f"{coffee} 途中で立ち寄った景色や香りまで、そっと思い出せるような時間でした。")
    if post_type == "写真" and emoji:
        extras.append(f"{camera} シャッターを切るたびに、小さな発見が増えていく感じが好きです。")

    closer = f"{cta}{' ' + wave if emoji else ''} {tone_ending_map[tone]}".strip()
    lines = [intro, keyword_sentence, location_sentence, *note_lines, *extras, deadline_sentence, closer]
    lines = [line for line in lines if line]
    return "\n".join(lines) if line_breaks else " ".join(lines)



def variant_text(base: str, mode: str) -> str:
    removals = [
        "やさしい余韻まで届いたらうれしいです",
        "楽しい気配まで一緒に届きますように",
        "気持ちごとまっすぐ届いたらうれしいです",
        "静かな温度感で受け取ってもらえたらうれしいです",
        "一歩踏み出すきっかけになれたらうれしいです",
    ]
    if mode == "short":
        text = base
        for phrase in removals:
            text = text.replace(phrase, "")
        return text.strip()
    if mode == "warm":
        return base + "\n小さなきっかけになれたらうれしいです。"
    return base + "\n気になる方はぜひチェックしてみてください。"



def run_self_tests() -> None:
    tag_result = build_hashtags("街ブラ", "X", "写真好き向け", "春, 桜, カメラ")
    assert "#街ブラ" in tag_result
    assert "#桜" in tag_result
    assert len(tag_result) <= 10

    caption_with_breaks = build_caption(
        platform="X",
        post_type="街ブラ",
        tone="明るい",
        theme="春の街歩き",
        keywords="春, 街歩き",
        cta="詳細はDMで",
        location="東京",
        deadline="",
        notes="やわらかな光がきれいでした。",
        emoji=True,
        line_breaks=True,
    )
    assert "\n" in caption_with_breaks

    caption_without_breaks = build_caption(
        platform="Instagram",
        post_type="写真",
        tone="やわらかい",
        theme="夕方の一枚",
        keywords="写真, 夕景",
        cta="コメント歓迎",
        location="上野",
        deadline="",
        notes="静かな時間でした。",
        emoji=False,
        line_breaks=False,
    )
    assert "\n" not in caption_without_breaks


run_self_tests()

if "theme" not in st.session_state:
    st.session_state.theme = "春の街歩きで見つけた花"
    st.session_state.keywords = "春, 街歩き, カメラ"
    st.session_state.notes = "何気ない風景の中にも、立ち止まりたくなる瞬間がある。\nそんな空気をことばにして残したい。"
    st.session_state.post_type = "街ブラ"
    st.session_state.platform = "X"
    st.session_state.tone = "やわらかい"
    st.session_state.cta = "詳細はDMで"
    st.session_state.location = "東京の下町"
    st.session_state.deadline = ""
    st.session_state.audience = "写真好き向け"
    st.session_state.emoji = True
    st.session_state.line_breaks = True
    st.session_state.selected_trend_id = None

st.title("SOLさん向け キャプション生成ツール")
st.caption("投稿タイプ、媒体、雰囲気、キーワードを入れると、Premium向けの冒頭設計つきキャプション案をまとめて作ります。")

left, right = st.columns([1, 1.1])

with left:
    st.subheader("入力")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.platform = st.selectbox("媒体", PLATFORMS, index=PLATFORMS.index(st.session_state.platform))
        st.session_state.tone = st.selectbox("雰囲気", TONES, index=TONES.index(st.session_state.tone))
        st.session_state.theme = st.text_input("テーマ", value=st.session_state.theme, placeholder="例: 春の街歩きで見つけた花")
        st.session_state.location = st.text_input("場所", value=st.session_state.location, placeholder="例: 谷中, 浅草, 上野")
        st.session_state.audience = st.selectbox("誰向けに寄せるか", AUDIENCES, index=AUDIENCES.index(st.session_state.audience))
    with col2:
        st.session_state.post_type = st.selectbox("投稿タイプ", POST_TYPES, index=POST_TYPES.index(st.session_state.post_type))
        st.session_state.cta = st.selectbox("CTA", CTAS, index=CTAS.index(st.session_state.cta))
        st.session_state.keywords = st.text_input("入れたいキーワード", value=st.session_state.keywords, placeholder="例: 春, 街歩き, カメラ")
        st.session_state.deadline = st.text_input("締切日や日時", value=st.session_state.deadline, placeholder="例: 10月31日 / 4月20日19時")
        st.session_state.emoji = st.toggle("絵文字を使う", value=st.session_state.emoji)
        st.session_state.line_breaks = st.toggle("改行を使う", value=st.session_state.line_breaks)

    st.session_state.notes = st.text_area(
        "補足メモ",
        value=st.session_state.notes,
        height=140,
        placeholder="写真の空気感や入れたい一言をメモ",
    )

    if st.button("雰囲気をランダム変更"):
        import random
        st.session_state.tone = random.choice(TONES)
        st.session_state.post_type = random.choice(POST_TYPES)
        st.session_state.platform = random.choice(PLATFORMS)
        st.session_state.cta = random.choice(CTAS)
        st.rerun()

base_caption = build_caption(
    platform=st.session_state.platform,
    post_type=st.session_state.post_type,
    tone=st.session_state.tone,
    theme=st.session_state.theme,
    keywords=st.session_state.keywords,
    cta=st.session_state.cta,
    location=st.session_state.location,
    deadline=st.session_state.deadline,
    notes=st.session_state.notes,
    emoji=st.session_state.emoji,
    line_breaks=st.session_state.line_breaks,
)

hashtags = build_hashtags(
    post_type=st.session_state.post_type,
    platform=st.session_state.platform,
    audience=st.session_state.audience,
    keywords=st.session_state.keywords,
)

opener280 = variant_text(base_caption, "short")[:280]
long_version = (
    base_caption
    + "\n\n"
    + (f"補足\n{st.session_state.notes}\n\n" if st.session_state.notes else "")
    + (
        "続きを読んでもらえるよう、流れを切らさずに言葉を重ねています。風景や空気感、そこで感じたことまで含めて届ける長文版です。"
        if st.session_state.platform == "X"
        else "投稿の余韻が残るよう、情景と気持ちを少し丁寧に広げた長文版です。"
    )
)

with right:
    st.subheader("出力")
    tab1, tab2, tab3 = st.tabs(["キャプション案", "ハッシュタグ", "トレンド取得"])

    with tab1:
        captions = [
            ("冒頭280字プレビュー", opener280, f"現在 {len(opener280)}文字"),
            ("通常版", base_caption, "そのまま投稿向け" if st.session_state.platform == "X" else "フィード投稿向け"),
            ("長文版", long_version, "Premium向けのしっかり語る版"),
            ("CTA強め版", variant_text(base_caption, "push"), "導線を少し強めた版"),
        ]
        for title, text, meta in captions:
            with st.container(border=True):
                st.markdown(f"#### {title}")
                st.caption(meta)
                st.text_area(title, value=text, height=220 if title == "長文版" else 160, key=f"caption_{title}")

    with tab2:
        with st.container(border=True):
            st.markdown("#### おすすめハッシュタグ")
            st.caption("投稿タイプ、媒体、キーワード、ターゲットから自動で組み合わせます。")
            st.write(" ".join(hashtags))
            st.text_area("ハッシュタグ一覧", value=" ".join(hashtags), height=100)

    with tab3:
        with st.container(border=True):
            st.markdown("#### Xトレンド候補")
            st.caption("ここでは取得イメージを再現しています。実運用ではX APIから取得して差し替える想定です。")
            trend_col1, trend_col2 = st.columns([0.45, 0.55])
            with trend_col1:
                region = st.selectbox("地域", TREND_REGIONS, index=TREND_REGIONS.index("東京"), key="trend_region")
            with trend_col2:
                trend_keyword = st.text_input("絞り込み", placeholder="例: 写真 / 街歩き / カフェ", key="trend_keyword")

            st.info("トレンドを見つけたら、そのままテーマとキーワードに反映できます。\n自動投稿ではなく【候補を見て選ぶ】流れにしてあるので、無理にトレンドへ乗りすぎない設計です。")

            trend_results = SAMPLE_TRENDS[region]
            if trend_keyword.strip():
                q = trend_keyword.strip().lower()
                trend_results = [
                    item for item in trend_results
                    if q in (item["name"] + " " + item["angle"] + " " + item["suggestedTheme"] + " " + item["suggestedKeywords"]).lower()
                ]

            for trend in trend_results:
                with st.container(border=True):
                    st.markdown(f"##### {trend['name']}")
                    st.write(f"投稿量: {trend['volume']} / 地域: {region}")
                    st.write(trend["angle"])
                    st.code(f"おすすめテーマ: {trend['suggestedTheme']}\nキーワード: {trend['suggestedKeywords']}")
                    if st.button(f"{trend['name']} を入力欄へ反映", key=f"trend_{trend['id']}"):
                        st.session_state.selected_trend_id = trend["id"]
                        st.session_state.theme = trend["suggestedTheme"]
                        st.session_state.keywords = trend["suggestedKeywords"]
                        st.session_state.post_type = "街ブラ"
                        st.session_state.platform = "X"
                        st.session_state.tone = "明るい"
                        st.session_state.notes = f"トレンド『{trend['name']}』をヒントに、自然に流れへ乗れる切り口に調整。\n{trend['angle']}"
                        st.rerun()

with st.expander("さらに便利にする候補"):
    st.write("・過去投稿とのかぶりチェック")
    st.write("・冒頭280字の刺さりチェック")
    st.write("・長文投稿の予約不可メモ")
    st.write("・募集投稿テンプレ保存")
    st.write("・CSV一括生成")
    st.write("・よく使うハッシュタグ辞書")

st.divider()
st.markdown("### GitHub と Streamlit で使う手順")
st.markdown(
    "1. このコードを `app.py` として保存する  \n"
    "2. `requirements.txt` に `streamlit` と書く  \n"
    "3. ローカルなら `streamlit run app.py` で起動  \n"
    "4. GitHub に push する  \n"
    "5. Streamlit Community Cloud でリポジトリ連携して公開する"
)
