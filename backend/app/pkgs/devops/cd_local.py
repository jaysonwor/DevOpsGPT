from ..devops.cd_interface import CDInterface
from subprocess import run, PIPE
#from config import WORKSPACE_PATH
'''
 Create CD
 https://docs.github.com/en/rest/deployments/deployments?apiVersion=2022-11-28#about-deployments
    
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/deployments \
  -d '{"ref":"topic-branch","payload":"{ \"deploy\": \"migrate\" }","description":"Deploy request from hubot"}'
  
  # GitHub CLI api
# https://cli.github.com/manual/gh_api

gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/OWNER/REPO/deployments \
   -f "ref=topic-branch" -f "payload={ "deploy": "migrate" }" -f "description=Deploy request from rastin"
  
'''

class CDLocal(CDInterface):
    def triggerCD(self, image, serviceInfo, cdConfig):
        command = 'gh api \
                --method POST \
                -H "Accept: application/vnd.github+json" \
                -H "X-GitHub-Api-Version: 2022-11-28" \
                /repos/OWNER/REPO?/deployments \
                -f "ref=topic-branch?" -f "payload={ "deploy": "migrate" }" -f "description=Deploy request from rastin" '

        try:
            cd_process = run( [ 'echo', 'hello' ], stdout=PIPE, stderr=PIPE )
        except Exception as e:
            raise Exception("Static code scan failed for unknown reasons: %s.", e)
        print ("CD_LOCAL Process : %s", cd_process.returncode)

        return "The pipeline cannot be run locally now, you can view the configuration and select tools such as gitlab.", False