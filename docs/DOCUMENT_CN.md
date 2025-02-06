# Quick Start

1. Clone the latest code or choose a released version, and prepare Python 3.7 or above.
2. Generate a configuration file: copy `env.yaml.tpl` and rename it to `env.yaml`.
3. Modify the configuration file: edit `env.yaml` and add necessary information such as GPT Token.
4. Run the service: execute `sh run.sh` on Linux or Mac, and double-click to run `run.bat` on Windows.
5. Access the service: access the service through a browser (the access address provided in the startup log, the default is http://127.0.0.1:8080).
6. Complete the demand development: follow the page instructions to complete the demand development, and view the generated code in the `./workspace` directory.

# Configuration Instructions

### Basic Configuration Class

1. FRONTEND_PORT, BACKEND_PORT: front-end port and back-end port
2. AICODER_ALLOWED_ORIGIN: The back-end allows cross-domain addresses, which are consistent with the front-end access address. Note: If you do not use 127.0.0.1 to access the website, please manually modify: apiUrl in frontend/static/js/coder.js
3. LANGUAGE: language
4. LLM_MODEL: model
5. GPT_KEYS: GPT's secret key, configure openai and azure interface information (replace sk-xxxx with your key). If you do not need a certain type of interface, please delete the corresponding element entirely (openai\azure). [Note] Do not add a comma after the last element in the array. You may need to enable a global proxy to access the API interface
6. USERS: login user configuration

### Git configuration

DevOpsGPT supports docking with Git. After enabling it, each development task can pull and push code from Git

1. GIT_ENABLED: Enable Git
2. GIT_URL: Configure your Git address, such as: https://github.com, https://gitlab.com
3. GIT_TOKEN: Configure your Git token, which can be obtained from: https://github.com/settings/tokens, https://gitlab.com/-/profile/personal_access_tokens
4. GIT_USERNAME: Git login username
5. GIT_EMAIL: Git email
6. APPS.service.git_path: Git path corresponding to the application, including group, such as: kuafuai/template_freestyleApp

### CI continuous integration tool configuration

DevOpsGPT supports docking with CI tools such as GitlabCI and GithubActions, and can trigger your pipeline after code submission.

Video introduction: https://www.bilibili.com/video/BV1C8411R7HD

<img src="files/ci.png" width="80%">

1. Complete the above "Git configuration"

2. GIT_API: Configure the address of Git API, for example: https://api.github.com

3. If it is Gitlab, you need to configure the pipeline, for example: [.gitlab-ci.yml](https://github.com/kuafuai/template_javaWebApp_backend/blob/master/.gitlab-ci.yml). At the same time, you need to configure Gitlab runner in Gitlab. For details, please refer to [Gitlab documentation](https://docs.gitlab.com/runner/)

4. If you are Github, you need to configure the pipeline, such as: [default.yaml](https://github.com/kuafuai/template_javaWebApp_backend/blob/master/.github/workflows/default.yaml). For details, please refer to [Github documentation](https://docs.github.com/en/actions/learn-github-actions)

### Automated deployment configuration

Automated deployment implements one-click deployment of developed applications to cloud services for everyone to access and use, truly realizing the transition from natural language requirements to working software!

Video introduction: https://www.bilibili.com/video/BV1cV4y1e7zg

The following takes Alibaba Cloud as an example for configuration introduction. Other cloud platforms are similar. Note: Using cloud platform resources may incur a small fee.

1. Create AccessKey on the cloud platform: Move the mouse to the avatar - Select AccessKey Management - Create AccessKey
2. According to the Kay created above, configure CD_ACCESS_KEY and CD_SECRET_KEY
3. CD_REGION: Set the deployment region. For example, if you deploy to Hong Kong, you can configure it as: cn-hongkong. Please consult the cloud platform customer service for details
4. CD_EIP: Create a public IP on the cloud platform for accessing the public network (note that the region must match CD_REGION)
5. CD_SECURITY: Create a security group on the cloud platform to open the external network port when starting the service
6. CD_SWITCH: Create a switch on the cloud platform

### APPS configuration

APPS is the application information we need to develop. The first step in using the product is to select a development application. During the development process, you need to analyze how the application should be designed and developed based on this information. In the open source version, this information needs to be maintained manually. We will provide AI intelligent analysis in the commercial version to automatically generate relevant information.

- app: application, including multiple services, such as backend service, frontend service, microservice
- name, intro: for display only
- service.name: service name, keep it unique
- service.git_workflow: Github workflow name, only effective when Github CI is turned on
- service.git_path: git path, needs to contain group, such as: kuafuai/template_freestyleApp
- service.base_prompt: basic starting prompt, which will affect the effect of task development
- service.intro: basic information of the service
- setpReqChooseLib (analyze the library packages used with service information)
- service.api_doc_url: interface document address, used to dynamically obtain interface documents
- service.api_doc: current interface document
- service.struct: file directory structure information of the service
- setp1Task (for molecular splitting tasks)
- service.lib: lib packages available for the service
- setpReqChooseLib (analyze which library packages are used with the library list)
- service.specification: lib package usage specification