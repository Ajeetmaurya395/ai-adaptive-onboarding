from urllib.parse import quote_plus


RESOURCE_LIBRARY = {
    "Python": {
        "documentation": ("Python Tutorial", "https://docs.python.org/3/tutorial/"),
        "free_video": ("YouTube: Python tutorial path", "https://www.youtube.com/results?search_query=python+tutorial"),
        "book": ("Automate the Boring Stuff with Python", "https://automatetheboringstuff.com/"),
        "practice": ("Exercism Python Track", "https://exercism.org/tracks/python"),
    },
    "AWS": {
        "documentation": ("AWS Documentation", "https://docs.aws.amazon.com/"),
        "free_video": ("YouTube: AWS tutorial path", "https://www.youtube.com/results?search_query=aws+tutorial"),
        "book": ("AWS Well-Architected Framework", "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html"),
        "practice": ("AWS Workshops", "https://workshops.aws/"),
    },
    "CloudFormation": {
        "documentation": ("AWS CloudFormation Docs", "https://docs.aws.amazon.com/cloudformation/"),
        "free_video": ("YouTube: CloudFormation tutorial path", "https://www.youtube.com/results?search_query=aws+cloudformation+tutorial"),
        "book": ("CloudFormation User Guide", "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html"),
        "practice": ("AWS Workshops", "https://workshops.aws/"),
    },
    "Docker": {
        "documentation": ("Docker Get Started", "https://docs.docker.com/get-started/"),
        "free_video": ("YouTube: Docker tutorial path", "https://www.youtube.com/results?search_query=docker+tutorial"),
        "book": ("Docker Deep Dive", ""),
        "practice": ("Play with Docker", "https://labs.play-with-docker.com/"),
    },
    "Kubernetes": {
        "documentation": ("Kubernetes Basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
        "free_video": ("YouTube: Kubernetes tutorial path", "https://www.youtube.com/results?search_query=kubernetes+tutorial"),
        "book": ("Kubernetes Up & Running", ""),
        "practice": ("Hello Minikube", "https://kubernetes.io/docs/tutorials/hello-minikube/"),
    },
    "Terraform": {
        "documentation": ("Terraform Tutorials", "https://developer.hashicorp.com/terraform/tutorials"),
        "free_video": ("YouTube: Terraform tutorial path", "https://www.youtube.com/results?search_query=terraform+tutorial"),
        "book": ("Terraform: Up & Running", ""),
        "practice": ("HashiCorp Learn Labs", "https://developer.hashicorp.com/terraform/tutorials"),
    },
    "CI/CD": {
        "documentation": ("GitHub Actions Docs", "https://docs.github.com/en/actions"),
        "free_video": ("YouTube: CI/CD tutorial path", "https://www.youtube.com/results?search_query=ci+cd+tutorial"),
        "book": ("GitHub Actions Study Path", "https://docs.github.com/en/actions/learn-github-actions"),
        "practice": ("GitHub Skills", "https://skills.github.com/"),
    },
    "Jenkins": {
        "documentation": ("Jenkins User Documentation", "https://www.jenkins.io/doc/"),
        "free_video": ("YouTube: Jenkins tutorial path", "https://www.youtube.com/results?search_query=jenkins+tutorial"),
        "book": ("Jenkins Tutorials", "https://www.jenkins.io/doc/tutorials/"),
        "practice": ("Jenkins Hands-on Tutorials", "https://www.jenkins.io/doc/tutorials/"),
    },
    "Prometheus": {
        "documentation": ("Prometheus Overview", "https://prometheus.io/docs/introduction/overview/"),
        "free_video": ("YouTube: Prometheus tutorial path", "https://www.youtube.com/results?search_query=prometheus+tutorial"),
        "book": ("Prometheus Documentation", "https://prometheus.io/docs/introduction/overview/"),
        "practice": ("Prometheus Tutorials", "https://prometheus.io/docs/tutorials/"),
    },
    "Microservices": {
        "documentation": ("Microservices Resource Guide", "https://martinfowler.com/microservices/"),
        "free_video": ("YouTube: Microservices tutorial path", "https://www.youtube.com/results?search_query=microservices+tutorial"),
        "book": ("Building Microservices", ""),
        "practice": ("Microservice Patterns", "https://microservices.io/patterns/index.html"),
    },
    "Git": {
        "documentation": ("Git Documentation", "https://git-scm.com/doc"),
        "free_video": ("YouTube: Git tutorial path", "https://www.youtube.com/results?search_query=git+tutorial"),
        "book": ("Pro Git", "https://git-scm.com/book/en/v2"),
        "practice": ("GitHub Skills", "https://skills.github.com/"),
    },
    "Leadership": {
        "documentation": ("Atlassian Leadership Guide", "https://www.atlassian.com/agile/project-management/team-leadership"),
        "free_video": ("YouTube: Engineering leadership path", "https://www.youtube.com/results?search_query=engineering+leadership+tutorial"),
        "book": ("The Manager's Path", ""),
        "practice": ("Leadership case-study prompts", "https://www.mindtools.com/"),
    },
}


def _generic_youtube(skill: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(skill + ' tutorial')}"


def _generic_documentation(skill: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(skill + ' official documentation')}"


def _generic_books(skill: str) -> str:
    return f"https://openlibrary.org/search?q={quote_plus(skill)}"


def build_learning_resources(skill: str, primary_course: dict | None = None) -> list[dict]:
    pack = RESOURCE_LIBRARY.get(skill, {})
    resources: list[dict] = []

    documentation = pack.get("documentation", (f"{skill} official documentation", _generic_documentation(skill)))
    doc_title, doc_url = documentation
    resources.append({"type": "Documentation", "title": doc_title, "url": doc_url, "cost": "Free"})

    resources.append({
        "type": "Free Video",
        "title": pack.get("free_video", ("YouTube learning path", _generic_youtube(skill)))[0],
        "url": pack.get("free_video", ("YouTube learning path", _generic_youtube(skill)))[1],
        "cost": "Free",
    })

    if primary_course:
        resources.append({
            "type": "Paid Course",
            "title": primary_course.get("title", primary_course.get("resource", f"{skill} course")),
            "url": primary_course.get("url", ""),
            "cost": "Paid",
        })

    book_title, book_url = pack.get("book", (f"{skill} study materials", _generic_books(skill)))
    resources.append({"type": "Book", "title": book_title, "url": book_url, "cost": "Mixed"})

    practice_title, practice_url = pack.get("practice", (f"{skill} practice resources", _generic_youtube(skill + " hands on")))
    resources.append({"type": "Practice", "title": practice_title, "url": practice_url, "cost": "Free"})

    return resources
