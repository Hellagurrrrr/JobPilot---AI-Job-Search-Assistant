from services.cv_service import extract_cv_from_pdf
from services.jd_service import extract_jd_from_url
from services.match_service import match_cv_to_jd

def main():
    cv = None
    jd = None

    file_path = input("请输入简历文件路径: ").strip()
    try:
        cv = extract_cv_from_pdf(file_path)
        print("\n===== CV 分析结果 =====")
        print(cv.model_dump_json(indent=2, ensure_ascii=False))
    except Exception as e:
        print("\n===== CV 分析失败 =====")
        print(e)

    url = input("请输入岗位链接: ").strip()
    try:
        jd = extract_jd_from_url(url)
        print("\n===== JD 分析结果 =====")
        print(jd.model_dump_json(indent=2, ensure_ascii=False))
    except Exception as e:
        print("\n===== JD 分析失败 =====")
        print(e)

    if cv is not None and jd is not None:
        try:
            match_result = match_cv_to_jd(cv, jd)
            print("\n===== 岗位匹配分析结果 =====")
            print(match_result.model_dump_json(indent=2, ensure_ascii=False))
        except Exception as e:
            print("\n===== 匹配分析失败 =====")
            print(e)

if __name__ == "__main__":
    main()