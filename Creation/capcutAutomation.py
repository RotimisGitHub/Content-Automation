import pyautogui
import subprocess

capCutPath = "/System/Volumes/Data/Applications/CapCut.app"
openCapCut = ['open', '-a', capCutPath]
openFullScreenScript = ['osascript', '-e',
                        'tell application "System Events" to keystroke "f" using {command down, control down}']

checkCapCutOpen = ['pgrep', capCutPath]
closeCapCut = ['killall', capCutPath]


def _completeClickObjective(commandList: list[dict]):
    for command in commandList:
        pyautogui.moveTo(command['x'], command['y'], duration=1)
        pyautogui.sleep(1)
        pyautogui.click(command['x'], command['y'])
        pyautogui.sleep(command['pause time'])

    return True


def openFullScreen():
    subprocess.run(openCapCut)
    pyautogui.sleep(30)
    subprocess.run(openFullScreenScript)
    pyautogui.sleep(3)


def createProjectAndImport(tempVideoFile: str):
    subprocess.run(openCapCut)
    pyautogui.sleep(3)
    pyautogui.hotkey("command", 'n')
    pyautogui.sleep(3)
    subprocess.run(openCapCut)
    pyautogui.sleep(3)
    pyautogui.hotkey("command", 'i')
    pyautogui.sleep(5)
    pyautogui.hotkey("command", 'shift', 'g')
    pyautogui.sleep(2)
    pyautogui.hotkey("delete")
    pyautogui.sleep(2)
    pyautogui.typewrite(tempVideoFile)
    pyautogui.hotkey("return")
    pyautogui.sleep(5)
    pyautogui.hotkey("return")
    pyautogui.sleep(5)


def addCaptions():
    addToTrackAction = ({"x": 248, "y": 255, "pause time": 12})
    clickTextAction = ({"x": 152, "y": 54, "pause time": 2})
    clickAutoCaptionAction = ({"x": 68, "y": 307, "pause time": 2})
    generateAutoCaptionAction = ({"x": 596, "y": 477, "pause time": 60})

    simultaneous_clicks = [addToTrackAction, clickTextAction, clickAutoCaptionAction, generateAutoCaptionAction]
    _completeClickObjective(simultaneous_clicks)


def completeCaptions(projectFullName: str):
    captionTemplateAction = ({"x": 1209, "y": 100, "pause time": 4})
    selectSpecificTemplateAction = ({"x": 1350, "y": 237, "pause time": 5})
    exportProjectAction = ({"x": 1396, "y": 17, "pause time": 5})
    shareContentInputAction = ({"x": 915, "y": 181, "pause time": 3})

    confirmExportAction = ({"x": 990, "y": 752, "pause time": 120})
    exitExportAction = ({"x": 911, "y": 752, "pause time": 3})

    simultaneous_clicks = [captionTemplateAction, selectSpecificTemplateAction, exportProjectAction,
                           shareContentInputAction]
    secondSimultaneousClicks = [confirmExportAction, exitExportAction]
    _completeClickObjective(simultaneous_clicks)
    pyautogui.hotkey("command", 'a', 'delete', interval=0.5)
    pyautogui.typewrite(projectFullName)
    pyautogui.sleep(2)
    _completeClickObjective(secondSimultaneousClicks)
    pyautogui.hotkey('command', 'q')
    subprocess.run(closeCapCut)
    print('completed entire video creation!!!')


def collectSubtitles(projectName: str, videoDirectory: str):
    openFullScreen()
    createProjectAndImport(videoDirectory)
    addCaptions()
    completeCaptions(projectName)
