import warnings
# 屏蔽所有 UserWarning 类型的警告
warnings.filterwarnings("ignore", category=UserWarning)

import argparse
import os
from document_manager import DocumentManager
from image_manager import ImageManager

def main():
    parser = argparse.ArgumentParser(description='Local Multimodal AI Agent')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 添加论文命令
    add_parser = subparsers.add_parser('add_paper', help='Add and classify a paper')
    add_parser.add_argument('path', help='Path to the paper PDF')
    add_parser.add_argument('--topics', help='Comma-separated list of topics')

    # 搜索论文命令
    search_paper_parser = subparsers.add_parser('search_paper', help='Search papers by query')
    search_paper_parser.add_argument('query', help='Search query')

    # 搜索图像命令
    search_image_parser = subparsers.add_parser('search_image', help='Search images by description')
    search_image_parser.add_argument('query', help='Image description query')

    #整理文件命令
    organize_parser = subparsers.add_parser('organize', help='Organize an existing messy folder')
    organize_parser.add_argument('path', help='Path to the messy folder containing PDFs')

    args = parser.parse_args()

    if args.command == 'add_paper':
        if not os.path.exists(args.path):
            print(f"Error: File {args.path} does not exist")
            return
        doc_manager = DocumentManager()
        topics = args.topics.split(',') if args.topics else []
        doc_manager.add_and_classify_paper(args.path, topics)

    elif args.command == 'search_paper':
        doc_manager = DocumentManager()
        results = doc_manager.search_papers(args.query)
        if results:
            print("Found papers:")
            for metadata in results:
                print(f"- {metadata['path']}")
        else:
            print("No papers found")

    elif args.command == 'search_image':
        img_manager = ImageManager()
        results = img_manager.search_images(args.query)
        if results:
            print("Found images:")
            for metadata in results:
                print(f"- {metadata['path']}")
        else:
            print("No images found")

    elif args.command == 'organize':
        doc_manager = DocumentManager()
        doc_manager.organize_folder(args.path)

if __name__ == '__main__':
    main()
