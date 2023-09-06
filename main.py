import re
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    result_arr = []
    with pdfplumber.open(pdf_path) as pdf_file:
        # Loop through each page and extract the text
        for page in pdf_file.pages:
            # Extract the text from the page
            result_arr.append(page.extract_text())

    return '\n'.join(result_arr)


def remove_matched_text(text: str, regex_list: list[str]) -> str:
    for regex in regex_list:
        pattern = re.compile(regex, flags=re.MULTILINE | re.DOTALL)
        text = pattern.sub('', text)
    return text


def get_csv_lines(ori_text: str) -> list[str]:
    pattern = r'(\d{4}-\d{2}-\d{2}\s.*?)(?=\d{4}-\d{2}-\d{2}\s|\Z)'
    matches = re.findall(pattern, ori_text, re.DOTALL)
    result = []
    for match in matches:
        lines = [item.strip() for item in match.strip().split('\n')]
        first = lines[0].split()
        rest_lines_content = '"' + '\n'.join(lines[1:]) + '"'
        last_2_line = get_last_2_line(lines[1:])
        last_line = lines[-1]
        result.append('\t'.join(first) + '\t' + rest_lines_content + '\t' + last_line + '\t' + last_2_line)

    return result


def get_last_2_line(lines):
    if len(lines) >= 2:
        return lines[-2]
    else:
        return '*****'


def pdf_to_csv(pdf_file_path: str, regex_list: list[str], header: list[str], output_csv_path: str):
    pdf_text = extract_text_from_pdf(pdf_file_path)
    cleaned_pdf_text = remove_matched_text(
        pdf_text,
        regex_list
    ).strip()
    csv_lines = get_csv_lines(cleaned_pdf_text)
    with open(output_csv_path, "w", encoding="utf-8") as file:
        file.write('\t'.join(header) + '\n')
        file.write('\n'.join(csv_lines))


if __name__ == '__main__':
    pdf_to_csv(pdf_file_path='in_out/ACCOUNT DETAILS CALLSELL.pdf',
               regex_list=[r'^账户号码.*?详细资料$',
                           r'打印日期.+?(\n\n|\Z)',
                           r'活期交易明细列表-网络版.+?\n\n'],
               header=['date', 'ref', 'debit', 'credit', 'balance', 'details', 'last_detail', 'last_2_detail'],
               output_csv_path='in_out/callsell.csv')
