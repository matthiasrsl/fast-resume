import argparse

from src.resume import Resume

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Fast resume : Quickly generate beautiful resumes from JSON.")
    argparser.add_argument("--resume", help="Name of the JSON file containing the resume data, without the extension.")
    argparser.add_argument("--template", help="Name of the template to use.", default="zeng")
    args = argparser.parse_args()

    resume = Resume(args.resume)
    resume.preprocess()
    resume.render(args.template)
