from urllib.parse import quote_plus


RESOURCE_LIBRARY = {
    "Python": {
        "documentation": ("Python Tutorial", "https://docs.python.org/3/tutorial/", "Official beginner-friendly guide covering core concepts and syntax."),
        "free_video": ("YouTube: Python tutorial path", "https://www.youtube.com/results?search_query=python+tutorial", "Curated video series for visual learning of Python basics."),
        "book": ("Automate the Boring Stuff with Python", "https://automatetheboringstuff.com/", "Practical book focused on real-world automation tasks."),
        "practice": ("Exercism Python Track", "https://exercism.org/tracks/python", "Hands-on coding exercises with mentor feedback."),
    },
    "AWS": {
        "documentation": ("AWS Documentation", "https://docs.aws.amazon.com/", "Comprehensive technical documentation for all AWS services."),
        "free_video": ("YouTube: AWS tutorial path", "https://www.youtube.com/results?search_query=aws+tutorial", "Detailed video walkthroughs of AWS core services."),
        "book": ("AWS Well-Architected Framework", "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html", "Best practices for designing secure and efficient cloud systems."),
        "practice": ("AWS Workshops", "https://workshops.aws/", "Self-paced labs provided by AWS for hands-on experience."),
    },
    "CloudFormation": {
        "documentation": ("AWS CloudFormation Docs", "https://docs.aws.amazon.com/cloudformation/", "Official guide for Infrastructure as Code on AWS."),
        "free_video": ("YouTube: CloudFormation tutorial path", "https://www.youtube.com/results?search_query=aws+cloudformation+tutorial", "Visual guides for writing and deploying stacks."),
        "book": ("CloudFormation User Guide", "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html", "Deep dive into template syntax and resource types."),
        "practice": ("AWS Workshops", "https://workshops.aws/", "Practical exercises for automating infrastructure deployment."),
    },
    "Docker": {
        "documentation": ("Docker Get Started", "https://docs.docker.com/get-started/", "Official introduction to containerization with Docker."),
        "free_video": ("YouTube: Docker tutorial path", "https://www.youtube.com/results?search_query=docker+tutorial", "Video guides for creating and managing containers."),
        "book": ("Docker Deep Dive", "", "Comprehensive guide to Docker internals and orchestration."),
        "practice": ("Play with Docker", "https://labs.play-with-docker.com/", "Interactive browser-based terminal for testing Docker."),
    },
    "Kubernetes": {
        "documentation": ("Kubernetes Basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "Official walkthrough of K8s cluster operations."),
        "free_video": ("YouTube: Kubernetes tutorial path", "https://www.youtube.com/results?search_query=kubernetes+tutorial", "Step-by-step videos for managing containerized apps."),
        "book": ("Kubernetes Up & Running", "", "Practical guide to building and running K8s clusters."),
        "practice": ("Hello Minikube", "https://kubernetes.io/docs/tutorials/hello-minikube/", "Local hands-on environment for learning K8s."),
    },
    "Terraform": {
        "documentation": ("Terraform Tutorials", "https://developer.hashicorp.com/terraform/tutorials", "Official HashiCorp learning paths for IaC."),
        "free_video": ("YouTube: Terraform tutorial path", "https://www.youtube.com/results?search_query=terraform+tutorial", "Visual tutorials for provider configuration and state."),
        "book": ("Terraform: Up & Running", "", "Guide to using Terraform for production-grade infrastructure."),
        "practice": ("HashiCorp Learn Labs", "https://developer.hashicorp.com/terraform/tutorials", "Interactive labs for multi-cloud deployment."),
    },
    "CI/CD": {
        "documentation": ("GitHub Actions Docs", "https://docs.github.com/en/actions", "Official documentation for automation workflows."),
        "free_video": ("YouTube: CI/CD tutorial path", "https://www.youtube.com/results?search_query=ci+cd+tutorial", "Video guides for pipeline design and best practices."),
        "book": ("GitHub Actions Study Path", "https://docs.github.com/en/actions/learn-github-actions", "Curated learning paths for workflow development."),
        "practice": ("GitHub Skills", "https://skills.github.com/", "Interactive courses built into GitHub directly."),
    },
    "Jenkins": {
        "documentation": ("Jenkins User Documentation", "https://www.jenkins.io/doc/", "Official user guide for the Jenkins automation server."),
        "free_video": ("YouTube: Jenkins tutorial path", "https://www.youtube.com/results?search_query=jenkins+tutorial", "Video lessons on job configuration and pipelines."),
        "book": ("Jenkins Tutorials", "https://www.jenkins.io/doc/tutorials/", "Practical examples for integrating Jenkins."),
        "practice": ("Jenkins Hands-on Tutorials", "https://www.jenkins.io/doc/tutorials/", "Step-by-step exercises for automated deployments."),
    },
    "Prometheus": {
        "documentation": ("Prometheus Overview", "https://prometheus.io/docs/introduction/overview/", "Official documentation for the monitoring system."),
        "free_video": ("YouTube: Prometheus tutorial path", "https://www.youtube.com/results?search_query=prometheus+tutorial", "Visual guides for metrics collection and alerting."),
        "book": ("Prometheus Documentation", "https://prometheus.io/docs/introduction/overview/", "Technical deep dive into the Prometheus ecosystem."),
        "practice": ("Prometheus Tutorials", "https://prometheus.io/docs/tutorials/", "Hands-on labs for setting up monitoring stacks."),
    },
    "Microservices": {
        "documentation": ("Microservices Resource Guide", "https://martinfowler.com/microservices/", "Seminal architectural guide by Martin Fowler."),
        "free_video": ("YouTube: Microservices tutorial path", "https://www.youtube.com/results?search_query=microservices+tutorial", "Detailed explanation of distributed system patterns."),
        "book": ("Building Microservices", "", "Key principles for designing and scaling microservices."),
        "practice": ("Microservice Patterns", "https://microservices.io/patterns/index.html", "Catalog of patterns for microservices architecture."),
    },
    "Git": {
        "documentation": ("Git Documentation", "https://git-scm.com/doc", "Official reference manual for Git version control."),
        "free_video": ("YouTube: Git tutorial path", "https://www.youtube.com/results?search_query=git+tutorial", "Visual guide for branching, merging, and staging."),
        "book": ("Pro Git", "https://git-scm.com/book/en/v2", "Comprehensive book covering basic to advanced Git usage."),
        "practice": ("GitHub Skills", "https://skills.github.com/", "Interactive projects to learn Git on the command line."),
    },
    "Leadership": {
        "documentation": ("Atlassian Leadership Guide", "https://www.atlassian.com/agile/project-management/team-leadership", "Best practices for leading agile engineering teams."),
        "free_video": ("YouTube: Engineering leadership path", "https://www.youtube.com/results?search_query=engineering+leadership+tutorial", "Interviews and talks from tech leadership experts."),
        "book": ("The Manager's Path", "", "Career guide for engineers transitioning into leadership."),
        "practice": ("Leadership case-study prompts", "https://www.mindtools.com/", "Scenario-based exercises for decision-making training."),
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

    documentation = pack.get("documentation", (f"{skill} official documentation", _generic_documentation(skill), "Search for official documentation."))
    doc_title, doc_url, doc_desc = documentation
    resources.append({"type": "Documentation", "title": doc_title, "url": doc_url, "description": doc_desc, "cost": "Free"})

    video_pack = pack.get("free_video", ("YouTube learning path", _generic_youtube(skill), "Search for community-provided video tutorials."))
    video_title, video_url, video_desc = video_pack
    resources.append({
        "type": "Free Video",
        "title": video_title,
        "url": video_url,
        "description": video_desc,
        "cost": "Free",
    })

    if primary_course:
        resources.append({
            "type": "Paid Course",
            "title": primary_course.get("title", primary_course.get("resource", f"{skill} course")),
            "url": primary_course.get("url", ""),
            "description": f"Curated high-quality learning from {primary_course.get('provider', 'trusted providers')}.",
            "cost": "Paid",
        })

    book_pack = pack.get("book", (f"{skill} study materials", _generic_books(skill), "Search for literature and academic resources."))
    book_title, book_url, book_desc = book_pack
    resources.append({"type": "Book", "title": book_title, "url": book_url, "description": book_desc, "cost": "Mixed"})

    practice_pack = pack.get("practice", (f"{skill} practice resources", _generic_youtube(skill + " hands on"), "Search for hands-on labs and practice environments."))
    practice_title, practice_url, practice_desc = practice_pack
    resources.append({"type": "Practice", "title": practice_title, "url": practice_url, "description": practice_desc, "cost": "Free"})

    return resources
