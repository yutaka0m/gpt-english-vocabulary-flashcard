from datetime import timezone, timedelta, datetime

import openai

model = "gpt-3.5-turbo"


# GPT-3 APIにリクエストを送信する関数
def send_request_to_gpt3_api(text, prompt_prefix):
    prompt = prompt_prefix + "\n" + text
    print(f"prompt: {prompt}")

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "あなたはTOEIC対策専門の英語の先生です."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    response_text = response.choices[0].message.content
    # 空白業があったら削除
    response_text = "\n".join(line for line in response_text.split("\n") if line.strip())

    consumed_tokens = response['usage']['total_tokens']

    print(f"gpt response: {response_text}")
    print(f"consumed token: {consumed_tokens}")

    return response_text, consumed_tokens


# ファイルを読み込んでGPT-3 APIにリクエストを送信し、結果をoutput.txtに書き込む
def main(prompt_prefix):
    def _send_request_to_gpt3_api(lines, output_file):
        request_text = "\n".join(lines)
        response_text, consumed_tokens = send_request_to_gpt3_api(request_text, prompt_prefix)
        output_file.write(response_text)
        output_file.write("\n")
        return consumed_tokens

    total_consumed_token = 0
    jst = timezone(timedelta(hours=+9))
    date = datetime.now(jst).strftime("%Y%m%d_%H%M%S")
    with open("input.txt", "r", encoding="utf-8") as input_file, open(f"output_{date}.txt", "a",
                                                                      encoding="utf-8") as output_file:
        lines = []
        for line in input_file:
            lines.append(line.strip())

            if len(lines) == 5:
                consumed_tokens = _send_request_to_gpt3_api(lines, output_file)
                total_consumed_token += consumed_tokens

                # 次の10行のためにlinesを空にします
                lines = []

        # 最後の10行未満の行がある場合
        if lines:
            consumed_tokens = _send_request_to_gpt3_api(lines, output_file)
            total_consumed_token += consumed_tokens

    print(f"total consume token: {total_consumed_token}")


if __name__ == '__main__':
    prompt_prefix = '''\
次の英単語,日本語訳の入力を参考にして、 英単語;日本語訳;日本語の品詞;英語の例文 を出力してください.
例文はTOEIC風の簡単なものにしてください.
英語の例文に日本語訳はつけないでください.
タイトルは出力しないでください.'''
    main(prompt_prefix)
