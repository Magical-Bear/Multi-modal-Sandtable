
from pypinyin import lazy_pinyin


def calculate_similarity(s1, s2):
    if s1 == s2:
        return 1.0
    s1, s2 = s1.lower(), s2.lower()
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return 1 - dp[n][m] / max(n, m)


# 将汉字转换为拼音
def get_pinyin(name):
    return ''.join(lazy_pinyin(name)).lower()


# 模糊查询
def fuzzy_search(query, wake_word_list=["智慧小锦", "社会小姐", "就会小姐", "是不小心", "就会了解", "会小点", "惠小姐"]):
    # 判断输入是汉字还是拼音
    if all('\u4e00' <= char <= '\u9fff' for char in query):  # 如果是汉字
        query_pinyin = get_pinyin(query)
    else:  # 如果是拼音
        query_pinyin = query.lower()
    for wake_word in wake_word_list:
        similarity = calculate_similarity(query_pinyin, get_pinyin(wake_word).lower())
        if similarity >= 0.5:
            break
    return similarity