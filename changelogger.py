import json
import subprocess

git_log_command = ['git', 'log', '--format=%B%H--DELIM--']
repo_url = 'https://github.com/BrandonGower-Winter/ABMECS/commit/'

def generate_changelog(version_type=2):
    process = subprocess.Popen(git_log_command,
                               stdout=subprocess.PIPE)

    stdout = process.communicate()

    commits = stdout[0].decode('UTF-8').split('--DELIM--\n')

    features = []
    performance = []
    fixes = []

    for commit in commits:
        try:
            msg, sha = commit.split('\n')

            if (msg.startswith('feat:')):
                msg = msg.replace('feat:', '')
                features.append((msg, sha))
            elif (msg.startswith('fix:')):
                msg = msg.replace('fix:', '')
                fixes.append((msg, sha))
            elif (msg.startswith('perf:')):
                msg = msg.replace('perf:', '')
                performance.append((msg, sha))

        except ValueError:
            continue


    # Get Version Data
    with open('package.json') as json_file:
        data = json.load(json_file)
        version = adjust_version(data['version'].split('.'), version_type)

    changelog = format_changelog_markdown(version, features, fixes, performance)
    print(changelog)


def adjust_version(version, version_type):
    if version_type == 0:
        return str(int(version[0]) + 1) + '.0.0'
    elif version_type == 1:
        return version[0] + '.' + str(int(version[1]) + 1) + '.0'
    else:
        return version[0] + '.' + version[1] + '.' + str(int(version[2]) + 1)


def format_changelog_markdown(version, features, fixes, performance):

    # Add Title
    changelog = '#Version: ' + version + '\n\n'

    # Add Features
    changelog += format_commits('Features', features)
    # Add Fixes
    changelog+= format_commits('Fixes', fixes)
    # Add Performance
    changelog += format_commits('Performance', performance)

    return changelog


def format_commits(title, list_of_commits):
    content = ''
    if len(list_of_commits) > 0:
        content = '##' + title + ':\n\n'

        for commit in list_of_commits:
            content += '- ' + commit[0] + '[' + commit[1] + '](' + repo_url + commit[1] + ')\n'

    return content


if __name__ == '__main__':
    generate_changelog()
