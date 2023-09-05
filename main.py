import sys

from src.resume import Resume

if __name__ == "__main__":
    resume = Resume(sys.argv[1])
    resume.preprocess()
    print(resume)  # noqa: T201
    # resume.render(sys.argv[2])
