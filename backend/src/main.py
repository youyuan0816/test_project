import argparse
import sys
import os

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='OpenCode Session Manager')
    parser.add_argument('--generate', action='store_true', help='生成 Excel 测试用例')
    parser.add_argument('--continue', dest='continue_file', metavar='EXCEL_FILE',
                        help='继续 session，读取 Excel 生成测试代码')
    args = parser.parse_args()

    if args.generate:
        from services.generator import generate_excel
        generate_excel()
    elif args.continue_file:
        from services.generator import continue_session
        continue_session(args.continue_file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
