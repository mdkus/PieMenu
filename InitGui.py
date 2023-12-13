# PieMenu widget for FreeCAD
#
# Copyright (C) 2022, 2023 mdkus @ FreeCAD
# Copyright (C) 2016, 2017 triplus @ FreeCAD
# Copyright (C) 2015,2016 looo @ FreeCAD
# Copyright (C) 2015 microelly <microelly2@freecadbuch.de>
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

# Attribution:
# http://forum.freecadweb.org/
# http://www.freecadweb.org/wiki/index.php?title=Code_snippets

global PIE_MENU_VERSION
PIE_MENU_VERSION = "1.2.7"

def pieMenuStart():
    import math
    import operator
    import platform
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtCore
    from PySide import QtGui
    import PieMenuLocator as locator

    # global status variables
    selectionTriggered = False
    contextPhase = False

    path = locator.path()
    respath = path + "/Resources/icons/"
    stylePath = path + "/Resources/style/"

    with open(stylePath + "Button.qss", "r") as file:
        styleButton = file.read()
    with open(stylePath + "MenuClose.qss", "r") as file:
        styleMenuClose = file.read()
    with open(stylePath + "Container.qss", "r") as file:
        styleContainer = file.read()
    with open(stylePath + "Combo.qss", "r") as file:
        styleCombo = file.read()
    with open(stylePath + "QuickMenu.qss", "r") as file:
        styleQuickMenu = file.read()
    with open(stylePath + "QuickMenuItem.qss", "r") as file:
        styleQuickMenuItem = file.read()

    iconClose = respath + "PieMenuClose.svg"
    iconMenu = respath + "PieMenuQuickMenu.svg"
    iconUp = respath + "PieMenuUp.svg"
    iconDown = respath + "PieMenuDown.svg"
    iconAdd = respath + "PieMenuAdd.svg"
    iconRemove = respath + "PieMenuRemove.svg"
    iconRename = respath + "PieMenuRename.svg"
    iconCopy = respath + "PieMenuCopy.svg"
    iconRemoveCommand = respath + "PieMenuRemoveCommand.svg"


    def remObsoleteParams():
        """Remove obsolete parameters from older versions."""
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramGet.RemBool("ContextPhase")

    def accessoriesMenu():
        """Add pie menu preferences to accessories menu."""
        pref = QtGui.QAction(mw)
        pref.setText("Pie menu")
        pref.setObjectName("PieMenu")
        pref.triggered.connect(onPreferences)
        try:
            import AccessoriesMenu
            AccessoriesMenu.addItem("PieMenu")
        except ImportError:
            a = mw.findChild(QtGui.QAction, "AccessoriesMenu")
            if a:
                a.menu().addAction(pref)
            else:
                mb = mw.menuBar()
                action = QtGui.QAction(mw)
                action.setObjectName("AccessoriesMenu")
                action.setIconText("Accessories")
                menu = QtGui.QMenu()
                action.setMenu(menu)
                menu.addAction(pref)

                def addMenu():
                    """Add accessories menu to the menu bar."""
                    mb.addAction(action)
                    action.setVisible(True)

                addMenu()
                mw.workbenchActivated.connect(addMenu)


    def onPreferences():
        """Open the preferences dialog."""
        onControl()


    def radiusSize(buttonSize):

        radius = str(math.trunc(buttonSize / 2))

        return "QToolButton {border-radius: " + radius + "px}"


    def iconSize(buttonSize):

        icon = buttonSize / 3 * 2

        return icon


    def closeButton(buttonSize=32):

        icon = iconSize(buttonSize)
        radius = radiusSize(buttonSize)

        button = QtGui.QToolButton()
        button.setProperty("ButtonX", 0)
        button.setProperty("ButtonY", 0)
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setIconSize(QtCore.QSize(icon, icon))
        button.setIcon(QtGui.QIcon(iconClose))
        button.setStyleSheet(styleMenuClose + radius)
        button.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        def onButton():

            PieMenuInstance.hide()

        button.clicked.connect(onButton)

        return button


    def quickMenu(buttonSize=20):

        icon = iconSize(buttonSize)
        radius = radiusSize(buttonSize)

        menu = QtGui.QMenu(mw)
        menu.setStyleSheet(styleQuickMenu)

        button = QtGui.QToolButton()
        button.setMenu(menu)
        button.setProperty("ButtonX", 0)
        button.setProperty("ButtonY", 32)
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setStyleSheet(styleMenuClose + radius)
        button.setIconSize(QtCore.QSize(icon, icon))
        button.setIcon(QtGui.QIcon(iconMenu))
        button.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        button.setPopupMode(QtGui.QToolButton
                            .ToolButtonPopupMode.InstantPopup)

        menuMode = QtGui.QMenu()
        menuMode.setTitle("Trigger")

        modeGroup = QtGui.QActionGroup(menuMode)
        modeGroup.setExclusive(True)

        actionPress = QtGui.QAction(modeGroup)
        actionPress.setText("Press")
        actionPress.setData("Press")
        actionPress.setCheckable(True)

        actionHover = QtGui.QAction(modeGroup)
        actionHover.setText("Hover")
        actionHover.setData("Hover")
        actionHover.setCheckable(True)

        menuMode.addAction(actionPress)
        menuMode.addAction(actionHover)

        actionContext = QtGui.QAction(menu)
        actionContext.setText("Context")
        actionContext.setCheckable(True)

        menuPieMenu = QtGui.QMenu()
        menuPieMenu.setTitle("PieMenu")

        pieGroup = QtGui.QActionGroup(menu)
        pieGroup.setExclusive(True)

        menuToolBar = QtGui.QMenu()
        menuToolBar.setTitle("ToolBar")
        menuToolBar.setStyleSheet(styleQuickMenuItem)

        toolbarGroup = QtGui.QMenu()

        toolbarGroupOps = QtGui.QActionGroup(toolbarGroup)
        toolbarGroupOps.setExclusive(True)

        prefAction = QtGui.QAction(menu)
        prefAction.setIconText("Preferences")

        prefButton = QtGui.QToolButton()
        prefButton.setDefaultAction(prefAction)

        prefButtonWidgetAction = QtGui.QWidgetAction(menu)
        prefButtonWidgetAction.setDefaultWidget(prefButton)

        def setChecked():
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

            if paramGet.GetString("TriggerMode") == "Hover":
                actionHover.setChecked(True)
            else:
                actionPress.setChecked(True)

            if paramGet.GetBool("EnableContext"):
                actionContext.setChecked(True)
            else:
                pass

        setChecked()

        def onModeGroup():
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            text = modeGroup.checkedAction().data()
            paramGet.SetString("TriggerMode", text)

            PieMenuInstance.hide()
            PieMenuInstance.showAtMouse(notKeyTriggered=True)

        modeGroup.triggered.connect(onModeGroup)

        def onActionContext():
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

            if actionContext.isChecked():
                paramGet.SetBool("EnableContext", True)
                contextList()
            else:
                paramGet.SetBool("EnableContext", False)

            addObserver()

        actionContext.triggered.connect(onActionContext)

        def pieList():
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
            indexList = paramIndexGet.GetString("IndexList")

            menuPieMenu.clear()

            if indexList:
                indexList = indexList.split(".,.")

                temp = []

                for i in indexList:
                    temp.append(int(i))

                indexList = temp
            else:
                indexList = []

            pieList = []

            for i in indexList:
                a = str(i)
                try:
                    pieName = paramIndexGet.GetString(a).decode("UTF-8")
                except AttributeError:
                    pieName = paramIndexGet.GetString(a)
                pieList.append(pieName)

            if not paramGet.GetBool("ToolBar"):
                try:
                    text = paramGet.GetString("CurrentPie").decode("UTF-8")
                except AttributeError:
                    text = paramGet.GetString("CurrentPie")
            else:
                text = None

            for i in pieList:
                action = QtGui.QAction(pieGroup)
                action.setText(i)
                action.setCheckable(True)

                if i == text:
                    action.setChecked(True)
                else:
                    pass

                menuPieMenu.addAction(action)

        menuPieMenu.aboutToShow.connect(pieList)

        def onPieGroup():
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

            paramGet.SetBool("ToolBar", False)
            paramGet.RemString("ToolBar")
            try:
                text = pieGroup.checkedAction().text().encode("UTF-8")
                paramGet.SetString("CurrentPie", text)
            except TypeError:
                text = pieGroup.checkedAction().text()
                paramGet.SetString("CurrentPie", text)

            PieMenuInstance.hide()
            PieMenuInstance.showAtMouse(notKeyTriggered=True)

        pieGroup.triggered.connect(onPieGroup)

        def onMenuToolBar():
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

            menuToolBar.clear()

            if paramGet.GetBool("ToolBar"):
                text = paramGet.GetString("ToolBar")
                if ": " in text:
                    toolbar_desc = text.split(": ")
                    text = toolbar_desc[1]
                else:
                    pass
            else:
                text = None

            for i in mw.findChildren(QtGui.QToolBar):

                commands = []

                for a in i.findChildren(QtGui.QToolButton):
                    try:
                        if not a.defaultAction().isSeparator():
                            commands.append(a.defaultAction())
                        else:
                            pass
                    except AttributeError:
                        pass

                if len(commands) != 0:
                    menu = QtGui.QMenu(i.windowTitle())
                    menu.aboutToShow.connect(lambda sender=menu: onMenuToolbarGroup(sender))
                    menuToolBar.addMenu(menu)
                else:
                    pass

        menuToolBar.aboutToShow.connect(onMenuToolBar)

        def isActualPie(text):

            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            if paramGet.GetBool("ToolBar"):
                entry = paramGet.GetString("ToolBar")
                if ": " in entry:
                    toolbar_desc = entry.split(": ")
                    idMenu = toolbar_desc[1]
                else:
                    idMenu = entry
                if idMenu == text:
                    return True;

            return False

        def onMenuToolbarGroup(sender):

            if not sender.actions():
                action = QtGui.QAction(sender)
                action.setText("Show")
                action.setData(sender.title())
                action.setCheckable(True)
                if isActualPie(sender.title()):
                    action.setChecked(True)
                sender.addAction(action)

                action = QtGui.QAction(sender)
                action.setText("Save")
                action.setData(sender.title())
                sender.addAction(action)

                sender.triggered.connect(lambda sender: onToolbarGroup(sender))

        def onToolbarGroup(sender):

            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            if sender.text() == "Show":
                paramGet.SetBool("ToolBar", True)
            elif sender.text() == "Save":
                newPieGroup = createPie(sender.data())
            else:
                return

            workbenches = []
            commands = []

            if sender.text() == "Save":
                # write persistent commands
                getGuiToolButtonData(sender.data(), None, commands, None)
                newPieGroup.SetString("ToolList", ".,.".join(commands))
            elif sender.text() == "Show":
                # write persistent toolbar and its workbenches
                getGuiToolButtonData(sender.data(), None, None, workbenches)
                toolbar_desc = ", ".join(workbenches)
                toolbar_desc = toolbar_desc + ': ' + sender.data()
                paramGet.SetString("ToolBar", toolbar_desc)            
                PieMenuInstance.hide()
                PieMenuInstance.showAtMouse(notKeyTriggered=True)                   

        toolbarGroup.triggered.connect(onToolbarGroup)

        def onPrefButton():

            PieMenuInstance.hide()
            onControl()

        prefButton.clicked.connect(onPrefButton)

        menu.addMenu(menuMode)
        menu.addAction(actionContext)
        menu.addSeparator()
        menu.addMenu(menuPieMenu)
        menu.addMenu(menuToolBar)
        menu.addSeparator()
        menu.addAction(prefButtonWidgetAction)

        return button


    class HoverButton(QtGui.QToolButton):

        def __init__(self, parent=None):
            super(HoverButton, self).__init__()

        def enterEvent(self, event):
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            mode = paramGet.GetString("TriggerMode")
            if self.defaultAction().isEnabled() and mode == "Hover":
                PieMenuInstance.hide()
                self.defaultAction().trigger()
            else:
                pass

        def mouseReleaseEvent(self, event):
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            mode = paramGet.GetString("TriggerMode")

            if self.defaultAction().isEnabled():
                PieMenuInstance.hide()
                self.defaultAction().trigger()
            else:
                pass


    class PieMenu:

        def __init__(self):

            self.radius = 100
            self.buttons = []
            self.buttonSize = 32
            self.menu = QtGui.QMenu(mw)
            self.menuSize = 0
            self.menu.setStyleSheet(styleContainer)
            self.menu.setWindowFlags(self.menu.windowFlags() | QtCore.Qt.FramelessWindowHint)
            self.menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            if compositingManager:
                pass
            else:
                self.menu.setAttribute(QtCore.Qt.WA_PaintOnScreen)

        def add_commands(self, commands, context=False):
            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

            for i in self.buttons:
                i.deleteLater()

            self.buttons = []

            if context:
                group = getGroup(mode=2)
            else:
                group = getGroup(mode=1)

            if len(commands) == 0:
                commandNumber = 1
            else:
                commandNumber = len(commands)

            valueRadius = group.GetInt("Radius")
            valueButton = group.GetInt("Button")

            if paramGet.GetBool("ToolBar"):
                valueRadius = 100
                valueButton = 32

            if valueRadius:
                self.radius = valueRadius
            else:
                self.radius = 100

            if valueButton:
                self.buttonSize = valueButton
            else:
                self.buttonSize = 32

            if commandNumber == 1:
                angle = 0
                buttonSize = self.buttonSize
            else:
                angle = 2 * math.pi / commandNumber
                buttonRadius = math.sin(angle / 2) * self.radius
                buttonSize = math.trunc(2 * buttonRadius / math.sqrt(2))

            angleStart = 3 * math.pi / 2 - angle

            if buttonSize > self.buttonSize:
                buttonSize = self.buttonSize
            else:
                pass

            radius = radiusSize(buttonSize)
            icon = iconSize(buttonSize)

            if windowShadow:
                pass
            else:
                self.menuSize = valueRadius * 2 + buttonSize + 4

                if self.menuSize < 90:
                    self.menuSize = 90
                else:
                    pass

                self.menu.setMinimumWidth(self.menuSize)
                self.menu.setMinimumHeight(self.menuSize)

            num = 1

            for i in commands:

                button = HoverButton()
                button.setParent(self.menu)
                button.setAttribute(QtCore.Qt.WA_Hover)
                button.setStyleSheet(styleButton + radius)
                button.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                button.setDefaultAction(commands[commands.index(i)])
                button.setGeometry(0, 0, buttonSize, buttonSize)
                button.setIconSize(QtCore.QSize(icon, icon))
                button.setProperty("ButtonX", self.radius *
                                   (math.cos(angle * num + angleStart)))
                button.setProperty("ButtonY", self.radius *
                                   (math.sin(angle * num + angleStart)))

                self.buttons.append(button)

                num = num + 1

            buttonQuickMenu = quickMenu()
            buttonQuickMenu.setParent(self.menu)
            self.buttons.append(buttonQuickMenu)

            buttonClose = closeButton()
            buttonClose.setParent(self.menu)
            self.buttons.append(buttonClose)

            if compositingManager:
                pass
            else:
                for i in self.buttons:
                    i.setAttribute(QtCore.Qt.WA_PaintOnScreen)

        def hide(self):
            for i in self.buttons:
                i.hide()

            self.menu.hide()

        def showAtMouse(self, notKeyTriggered=False):

            nonlocal selectionTriggered
            nonlocal contextPhase
            global lastPosX
            global lastPosY

            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

            enableContext = paramGet.GetBool("EnableContext")

            if contextPhase:
                sel = Gui.Selection.getSelectionEx()
                if not sel:
                    self.hide()
                    contextPhase = False
                    updateCommands()
                elif not enableContext:
                    self.hide()
                    updateCommands()
                else:
                    updateCommands(context=True)
            else:
                updateCommands()

            if self.menu.isVisible():
                self.hide()
            else:
                if windowShadow:
                    pos = mw.mapFromGlobal(QtGui.QCursor.pos())
                    if notKeyTriggered:
                        if contextPhase:
                            # special case treatment
                            if selectionTriggered:
                                selectionTriggered = False
                            else:
                                pos.setX(lastPosX)
                                pos.setY(lastPosY)
                            lastPosX = pos.x()
                            lastPosY = pos.y()
                        else:
                            pos.setX(lastPosX)
                            pos.setY(lastPosY)
                    else:
                        lastPosX = pos.x()
                        lastPosY = pos.y()

                    self.menu.popup(QtCore.QPoint(mw.pos()))
                    self.menu.setGeometry(mw.geometry())

                    for i in self.buttons:
                        i.move(i.property("ButtonX") + pos.x() - i.width() / 2,
                               i.property("ButtonY") + pos.y() - i.height() / 2)

                        i.setVisible(True)

                    for i in self.buttons:
                        i.repaint()
                else:
                    pos = QtGui.QCursor.pos()
                    if notKeyTriggered:
                        if contextPhase:
                            # special case treatment
                            if selectionTriggered:
                                selectionTriggered = False
                            else:
                                pos.setX(lastPosX)
                                pos.setY(lastPosY)
                            lastPosX = pos.x()
                            lastPosY = pos.y()
                        else:
                            pos.setX(lastPosX)
                            pos.setY(lastPosY)
                    else:
                        lastPosX = pos.x()
                        lastPosY = pos.y()

                    for i in self.buttons:
                        i.move(i.property("ButtonX") + (self.menuSize - i.size().width()) / 2,
                               i.property("ButtonY") + (self.menuSize - i.size().height()) / 2)

                        i.setVisible(True)

                    self.menu.popup(QtCore.QPoint(pos.x() - self.menuSize / 2, pos.y() - self.menuSize / 2))


    sign = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        }


    def contextList():
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")

        contextAll.clear()

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        for i in indexList:
            a = str(i)
            group = paramIndexGet.GetGroup(a)
            groupContext = group.GetGroup("Context")

            if groupContext.GetBool("Enabled"):

                current = {}

                current["Index"] = a

                current["VertexSign"] = groupContext.GetString("VertexSign")
                current["VertexValue"] = groupContext.GetInt("VertexValue")

                current["EdgeSign"] = groupContext.GetString("EdgeSign")
                current["EdgeValue"] = groupContext.GetInt("EdgeValue")

                current["FaceSign"] = groupContext.GetString("FaceSign")
                current["FaceValue"] = groupContext.GetInt("FaceValue")

                current["ObjectSign"] = groupContext.GetString("ObjectSign")
                current["ObjectValue"] = groupContext.GetInt("ObjectValue")

                contextAll[i] = current

            else:
                pass


    def getContextPie(v, e, f, o):
        global globalContextPie
        global globalIndexPie

        globalContextPie = False
        globalIndexPie = None

        for i in contextAll:

            current = contextAll[i]

            def vertex():
                if sign[current["VertexSign"]](v, current["VertexValue"]):
                    edge()
                else:
                    pass

            def edge():
                if sign[current["EdgeSign"]](e, current["EdgeValue"]):
                    face()
                else:
                    pass

            def face():
                if sign[current["FaceSign"]](f, current["FaceValue"]):
                    obj()
                else:
                    pass

            def obj():
                if sign[current["ObjectSign"]](o, current["ObjectValue"]):
                    global globalContextPie
                    global globalIndexPie

                    globalContextPie = "True"
                    globalIndexPie = current["Index"]
                else:
                    pass

            vertex()

        if globalContextPie == "True":
            return globalIndexPie
        else:
            return None


    def listTopo():

        nonlocal selectionTriggered
        nonlocal contextPhase

        sel = Gui.Selection.getSelectionEx()
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")

        vertexes = 0
        edges = 0
        faces = 0
        objects = 0

        allList = []

        for i in sel:
            if not i.SubElementNames:
                objects = objects + 1
            else:
                for a in i.SubElementNames:
                    allList.append(a)

        for i in allList:
            if i.startswith('Vertex'):
                vertexes = vertexes + 1
            elif i.startswith('Edge'):
                edges = edges + 1
            elif i.startswith('Face'):
                faces = faces + 1
            else:
                pass

        pieIndex = getContextPie(vertexes,
                                 edges,
                                 faces,
                                 objects)

        if pieIndex:
            try:
                pieName = paramIndexGet.GetString(pieIndex).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(pieIndex)
            try:
                paramGet.SetString("ContextPie", pieName.encode("UTF-8"))
            except TypeError:
                paramGet.SetString("ContextPie", pieName)
            contextPhase = True

            updateCommands(context=True)
            PieMenuInstance.hide()
            selectionTriggered = True
            PieMenuInstance.showAtMouse(notKeyTriggered=True)
        else:
            pass


    class SelObserver:

        def addSelection(self, doc, obj, sub, pnt):

            listTopo()

        def removeSelection(self, doc, obj, sub):

            listTopo()


    def addObserver():
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")

        if paramGet.GetBool("EnableContext"):
            Gui.Selection.addObserver(selObserver)
        else:
            Gui.Selection.removeObserver(selObserver)


    def getGuiActionMapAll():

        actions = {}
        duplicates = []

        for i in mw.findChildren(QtGui.QAction):
            if i.objectName() is not None:
                if i.objectName() != "" and i.icon():
                    if i.objectName() in actions:
                        if i.objectName() not in duplicates:
                            duplicates.append(i.objectName())
                        else:
                            pass
                    else:
                        actions[i.objectName()] = i
                else:
                    pass
            else:
                pass

        for d in duplicates:
            del actions[d]

        return actions


    def extractWorkbench(command):

        cmd_parts = command.split("_")
        if cmd_parts[0] == "":
            workbench = "None"
        else:
            workbench = cmd_parts[0]

        return workbench


    def getActionData(action, actions, commands, workbenches):

        if not action.icon():
            return
        if actions is not None:
            if action in actions:
                pass
            else:
                actions.append(action)
        if commands is None and workbenches is None:
            return

        command = action.objectName()
        if len(command) == 0:
            workbench = "None"
        else:
            if commands is not None:
                if command in commands:
                    pass
                else:
                    commands.append(command)
            workbench = extractWorkbench(command)

        if workbenches is not None:
            if not workbench in workbenches:
                workbenches.append(workbench)


    def getGuiToolButtonData(idToolBar, actions, commands, workbenches):

        actionMapAll = getGuiActionMapAll()
        for i in actionMapAll:
            action = actionMapAll[i]
            for widgets in action.associatedWidgets():
                if widgets.objectName() == idToolBar:
                    getActionData(action, actions, commands, workbenches)


    def actualizeWorkbenchActions(actions, toolList, actionMap):
        for i in toolList:
            # rule out special case: there has to be an entry
            if i == "":
                pass
            elif i in actionMap:
                if not actionMap[i] in actions:
                    actions.append(actionMap[i])
            else:
                cmd_parts = i.split("_")
                # rule out special case: unknown Std action
                if cmd_parts[0] == "Std":
                    pass
                else:
                    # match special cases
                    # Fem workbench
                    if cmd_parts[0] == "FEM":
                        cmd_parts[0] = "Fem"
                    # Sheet Metal workbench
                    if cmd_parts[0][:2] == "SM":
                        cmd_parts[0] = cmd_parts[0][:2]

                    cmdWb = cmd_parts[0] + "Workbench"
                    # after workbench activation actionMap has to be actualized
                    Gui.activateWorkbench(cmdWb)
                    return True

        return False


    def updateCommands(context=False):

        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")

        if paramGet.GetBool("ToolBar") and context is False:

            paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
            toolbar = paramGet.GetString("ToolBar")

            if ": " in toolbar:
                toolbar_desc = toolbar.split(": ")
                toolbar = toolbar_desc[1]
                workbenches = toolbar_desc[0]
                workbenches = workbenches.split(", ")
                lastWorkbench = Gui.activeWorkbench()

                for i in workbenches:
                    # rule out special cases
                    if i == "None" or i == "Std":
                        pass
                    else:
                        # match special cases
                        # Fem workbench
                        if i == "FEM":
                            i = "Fem"
                        # Sheet Metal workbench
                        if i[:2] == "SM":
                            i = i[:2]

                        Gui.activateWorkbench(i + "Workbench")

                Gui.activateWorkbench(lastWorkbench.__class__.__name__)
            else:
                pass

            actions = []
            getGuiToolButtonData(toolbar, actions, None, None)

        else:

            if indexList:
                indexList = indexList.split(".,.")

                temp = []

                for i in indexList:
                    temp.append(int(i))

                indexList = temp
            else:
                indexList = []

            if context:
                try:
                    text = paramGet.GetString("ContextPie").decode("UTF-8")
                except AttributeError:
                    text = paramGet.GetString("ContextPie")
            else:
                try:
                    text = paramGet.GetString("CurrentPie").decode("UTF-8")
                except AttributeError:
                    text = paramGet.GetString("CurrentPie")

            toolList = None

            for i in indexList:
                a = str(i)
                try:
                    pie = paramIndexGet.GetString(a).decode("UTF-8")
                except AttributeError:
                    pie = paramIndexGet.GetString(a)
                if pie == text:
                    group = paramIndexGet.GetGroup(a)
                    toolList = group.GetString("ToolList")
                else:
                    pass

            if toolList:
                toolList = toolList.split(".,.")
            else:
                toolList = []

            actions = []

            actionMapAll = getGuiActionMapAll()
            lastWorkbench = Gui.activeWorkbench()

            while actualizeWorkbenchActions(actions, toolList, actionMapAll):
                actionMapAll = getGuiActionMapAll()
            else:
                pass

            Gui.activateWorkbench(lastWorkbench.__class__.__name__)

        PieMenuInstance.add_commands(actions, context)


    def getGroup(mode=0):
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")

        if mode == 2:
            try:
                text = paramGet.GetString("ContextPie").decode("UTF-8")
            except AttributeError:
                text = paramGet.GetString("ContextPie")
        elif mode == 1:
            try:
                text = paramGet.GetString("CurrentPie").decode("UTF-8")
            except AttributeError:
                text = paramGet.GetString("CurrentPie")
        else:
            text = cBox.currentText()

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        group = None

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)

            if pie == text:
                group = paramIndexGet.GetGroup(a)
            else:
                pass

        if group:
            pass
        else:
            if 0 in indexList:
                group = paramIndexGet.GetGroup("0")
            else:
                setDefaultPie()
                updateCommands()
                group = paramIndexGet.GetGroup("0")

        return group

    buttonListWidget = QtGui.QListWidget()
    buttonListWidget.setHorizontalScrollBarPolicy(QtCore
                                                  .Qt.ScrollBarAlwaysOff)


    def buttonList():

        group = getGroup()
        toolList = group.GetString("ToolList")

        if toolList:
            toolList = toolList.split(".,.")
        else:
            toolList = []

        actionMapAll = getGuiActionMapAll()

        buttonListWidget.blockSignals(True)

        buttonListWidget.clear()

        workbenches = []
        lastWorkbench = Gui.activeWorkbench()

        for i in toolList:
            if i not in actionMapAll:
                # rule out special case: there has to be an entry
                if i == "":
                    pass
                else:
                    cmd_parts = i.split("_")
                    if cmd_parts[0] not in workbenches:
                        # rule out special case: unknown Std action
                        if cmd_parts[0] == "Std":
                            pass
                        else:
                            # treatment of special cases
                            # Fem workbench
                            if cmd_parts[0] == "FEM":
                                cmd_parts[0] = "Fem"
                            # Sheet Metal workbench
                            if cmd_parts[0][:2] == "SM":
                                cmd_parts[0] = cmd_parts[0][:2]
                            workbenches.append(cmd_parts[0])
                            Gui.activateWorkbench(cmd_parts[0] + "Workbench")
                    else:
                        pass
            else:
                pass

        Gui.activateWorkbench(lastWorkbench.__class__.__name__)
        actionMapAll = getGuiActionMapAll()

        for i in toolList:
            if i in actionMapAll:
                item = QtGui.QListWidgetItem(buttonListWidget)
                item.setData(QtCore.Qt.UserRole, i)
                item.setText(actionMapAll[i].text().replace("&", ""))
                item.setIcon(actionMapAll[i].icon())
            else:
                pass

        buttonListWidget.blockSignals(False)


    cBox = QtGui.QComboBox()
    cBox.setMinimumHeight(30)


    def cBoxUpdate():
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        pieList = []

        for i in indexList:
            a = str(i)
            try:
                pieList.append(paramIndexGet.GetString(a).decode("UTF-8"))
            except AttributeError:
                pieList.append(paramIndexGet.GetString(a))

        duplicates = []
        for i in pieList:            
            if i == currentPie:
                pass
            else:
                duplicates.append(i)
        duplicates.append(currentPie)
        pieList = duplicates

        pieList.reverse()

        cBox.blockSignals(True)

        cBox.clear()

        for i in pieList:
            cBox.insertItem(0, i)

        cBox.blockSignals(False)

        onPieChange()


    def onPieChange():
        buttonList()
        toolList()
        setDefaults()
        setCheckContext()

    cBox.currentIndexChanged.connect(onPieChange)

    buttonAddPieMenu = QtGui.QToolButton()
    buttonAddPieMenu.setIcon(QtGui.QIcon(iconAdd))
    buttonAddPieMenu.setToolTip("Add new pie menu")
    buttonAddPieMenu.setMinimumHeight(30)
    buttonAddPieMenu.setMinimumWidth(30)


    def inputTextDialog(title):

        info1 = "Please insert menu name"
        info2 = "Menu already exists"

        d = QtGui.QInputDialog(pieMenuDialog)
        d.setModal(True)
        d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
        text, ok = QtGui.QInputDialog.getText(pieMenuDialog,
                                              title,
                                              info1)
        if not ok:
            return text, ok

        while not text:
            text, ok = QtGui.QInputDialog.getText(pieMenuDialog,
                                              title,
                                              info1)
            if not ok:
                return text, ok
            else:
                pass

        index = cBox.findText(text)
        info = info2

        while index != -1:
            d = QtGui.QInputDialog(pieMenuDialog)
            d.setModal(True)
            d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
            text, ok = QtGui.QInputDialog.getText(pieMenuDialog,
                                                  title,
                                                  info)
            if ok:
                if text:
                    index = cBox.findText(text)
                    info = info2
                else:
                    info = info1
            else:
                return text, ok

        return text, ok


    def splitIndexList(indexList):

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        return indexList


    def createPie(text):


        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)

        pieList = []

        for i in indexList:
            a = str(i)
            pieList.append(paramIndexGet.GetString(a))

        if text.encode('UTF-8') in pieList:
            pass
        elif not text:
            pass
        else:

            if text == "restore_default_pie" and text.lower():
                setDefaultPie(restore=True)
            else:
                x = 1

                while x in indexList and x < 999:
                    x = x + 1
                else:
                    indexNumber = x

                indexList.append(indexNumber)

                temp = []

                for i in indexList:
                    temp.append(str(i))

                indexList = temp

                paramIndexGet.SetString("IndexList", ".,.".join(indexList))

                indexNumber = str(indexNumber)
                try:
                    paramIndexGet.SetString(indexNumber, text.encode('UTF-8'))
                except TypeError:
                    paramIndexGet.SetString(indexNumber, text)

            cBoxUpdate()

        return paramIndexGet.GetGroup(indexNumber)


    def onButtonAddPieMenu():

        text, ok = inputTextDialog("New menu")
        if not ok:
            return

        createPie(text)


    buttonAddPieMenu.clicked.connect(onButtonAddPieMenu)

    buttonRemovePieMenu = QtGui.QToolButton()
    buttonRemovePieMenu.setIcon(QtGui.QIcon(iconRemove))
    buttonRemovePieMenu.setToolTip("Remove current pie menu")
    buttonRemovePieMenu.setMinimumHeight(30)
    buttonRemovePieMenu.setMinimumWidth(30)


    def onButtonRemovePieMenu():
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        try:
            contextPie = paramGet.GetString("ContextPie").decode("UTF-8")
        except AttributeError:
            contextPie = paramGet.GetString("ContextPie")

        text = cBox.currentText()

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                indexList.remove(i)

                temp = []

                for i in indexList:
                    temp.append(str(i))

                indexList = temp

                paramIndexGet.SetString("IndexList", ".,.".join(indexList))

                paramIndexGet.RemGroup(a)
                paramIndexGet.RemString(a)
                # special case treatment                                             
                if pie == currentPie:
                    currentPie = "Default"
                    try:
                        paramGet.SetString("CurrentPie", currentPie.encode('UTF-8'))
                    except TypeError:
                        paramGet.SetString("CurrentPie", currentPie)
                if pie == contextPie:
                        paramGet.RemString("ContextPie")
            else:
                pass

        cBoxUpdate()

        if cBox.currentIndex() == -1:
            setDefaultPie()
            cBoxUpdate()
        else:
            pass

    buttonRemovePieMenu.clicked.connect(onButtonRemovePieMenu)

    buttonRenamePieMenu = QtGui.QToolButton()
    buttonRenamePieMenu.setToolTip("Rename current pie menu")
    buttonRenamePieMenu.setIcon(QtGui.QIcon(iconRename))
    buttonRenamePieMenu.setMinimumHeight(30)
    buttonRenamePieMenu.setMinimumWidth(30)


    def onButtonRenamePieMenu():

        text, ok = inputTextDialog("Rename menu")
        if not ok:
            return

        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        currentText = cBox.currentText()

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == currentText:
                try:
                    paramIndexGet.SetString(a, text.encode('UTF-8'))
                except TypeError:
                    paramIndexGet.SetString(a, text)
                if pie == currentPie:
                    try:
                        paramGet.SetString("CurrentPie", text.encode('UTF-8'))
                    except TypeError:
                        paramGet.SetString("CurrentPie", text)
                else:
                    pass
        cBoxUpdate()

    buttonRenamePieMenu.clicked.connect(onButtonRenamePieMenu)    

    buttonCopyPieMenu = QtGui.QToolButton()
    buttonCopyPieMenu.setToolTip("Copy current pie menu")
    buttonCopyPieMenu.setIcon(QtGui.QIcon(iconCopy))
    buttonCopyPieMenu.setMinimumHeight(30)
    buttonCopyPieMenu.setMinimumWidth(30)


    def getCurrentMenuIndex(currentMenuName):

        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)

        for i in indexList:
            a = str(i)
            indexName = paramIndexGet.GetString(a)
            if indexName == currentMenuName:
                return a;

        return "-1"

    def copyIndexParams(grpOrg, grpCopy):

        valButOrg = grpOrg.GetInt("Button")
        valRadOrg = grpOrg.GetInt("Radius")
        tbOrg = grpOrg.GetString("ToolList")

        grpCopy.SetInt("Button", valButOrg)
        grpCopy.SetInt("Radius", valRadOrg)
        grpCopy.SetString("ToolList", tbOrg)

    def copyContextParams(grpOrg, grpCopy):

        grpCntOrg = grpOrg.GetGroup("Context")
        grpCntCopy = grpCopy.GetGroup("Context")

        enabledOrg = grpCntOrg.GetBool("Enabled")
        vtxSgnOrg = grpCntOrg.GetString("VertexSign")
        vtxValOrg = grpCntOrg.GetInt("VertexValue")
        edgSgnOrg = grpCntOrg.GetString("EdgeSign")
        edgValOrg = grpCntOrg.GetInt("EdgeValue")
        fceSgnOrg = grpCntOrg.GetString("FaceSign")
        fceValOrg = grpCntOrg.GetInt("FaceValue")
        objSgnOrg = grpCntOrg.GetString("ObjectSign")
        objValOrg = grpCntOrg.GetInt("ObjectValue")

        grpCntCopy.SetBool("Enabled", enabledOrg)
        grpCntCopy.SetString("VertexSign", vtxSgnOrg)
        grpCntCopy.SetInt("VertexValue", vtxValOrg)
        grpCntCopy.SetString("EdgeSign", edgSgnOrg)
        grpCntCopy.SetInt("EdgeValue", edgValOrg)
        grpCntCopy.SetString("FaceSign", fceSgnOrg)
        grpCntCopy.SetInt("FaceValue", fceValOrg)
        grpCntCopy.SetString("ObjectSign", objSgnOrg)
        grpCntCopy.SetInt("ObjectValue", objValOrg)


    def onButtonCopyPieMenu():

        text, ok = inputTextDialog("Copy menu")
        if not ok:
            return

        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)

        currentMenuName = cBox.currentText()
        indexOrg = getCurrentMenuIndex(currentMenuName)

        pieList = []

        for i in indexList:
            a = str(i)
            pieList.append(paramIndexGet.GetString(a))

        if text.encode('UTF-8') in pieList:
            pass
        elif not text:
            pass
        else:
            x = 1

            while x in indexList and x < 999:
                x = x + 1
            else:
                indexCopy = x

            indexList.append(indexCopy)

            temp = []

            for i in indexList:
                temp.append(str(i))

            indexList = temp

            paramIndexGet.SetString("IndexList", ".,.".join(indexList))

            indexCopy = str(indexCopy)
            grpOrg = paramIndexGet.GetGroup(indexOrg)
            grpCopy = paramIndexGet.GetGroup(indexCopy)
            copyIndexParams(grpOrg, grpCopy)
            copyContextParams(grpOrg, grpCopy)

            try:
                paramIndexGet.SetString(indexCopy, text.encode('UTF-8'))
            except TypeError:
                paramIndexGet.SetString(indexCopy, text)

        cBoxUpdate()

    buttonCopyPieMenu.clicked.connect(onButtonCopyPieMenu)

    labelRadius = QtGui.QLabel("Pie size")
    spinRadius = QtGui.QSpinBox()
    spinRadius.setMaximum(9999)
    spinRadius.setMinimumWidth(70)


    def onSpinRadius():
        group = getGroup()
        value = spinRadius.value()
        group.SetInt("Radius", value)

    spinRadius.valueChanged.connect(onSpinRadius)

    labelButton = QtGui.QLabel("Button size")
    spinButton = QtGui.QSpinBox()
    spinButton.setMaximum(999)
    spinButton.setMinimumWidth(70)


    def onSpinButton():
        group = getGroup()
        value = spinButton.value()
        group.SetInt("Button", value)

    spinButton.valueChanged.connect(onSpinButton)

    toolListWidget = QtGui.QListWidget()
    toolListWidget.setSortingEnabled(True)
    toolListWidget.sortItems(QtCore.Qt.AscendingOrder)
    toolListWidget.setHorizontalScrollBarPolicy(QtCore
                                                .Qt.ScrollBarAlwaysOff)


    def toolList():

        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")

        text = cBox.currentText()

        actionMapAll = getGuiActionMapAll()

        toolListWidget.blockSignals(True)
        toolListWidget.clear()

        for i in actionMapAll:
            item = QtGui.QListWidgetItem(toolListWidget)
            item.setText(actionMapAll[i].text().replace("&", ""))
            item.setIcon(actionMapAll[i].icon())
            item.setCheckState(QtCore.Qt.CheckState(0))
            item.setData(QtCore.Qt.UserRole, actionMapAll[i].objectName())

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:

            indexList = []

        toolListOn = None

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolListOn = group.GetString("ToolList")
            else:
                pass

        if toolListOn:
            toolListOn = toolListOn.split(".,.")
        else:
            toolListOn = []

        items = []
        for index in range(toolListWidget.count()):
            items.append(toolListWidget.item(index))

        for i in items:
            if i.data(QtCore.Qt.UserRole) in toolListOn:
                i.setCheckState(QtCore.Qt.CheckState(2))
            else:
                pass

        toolListWidget.blockSignals(False)


    def onToolListWidget():
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")

        text = cBox.currentText()

        items = []
        for index in range(toolListWidget.count()):
            items.append(toolListWidget.item(index))

        checkListOn = []
        checkListOff = []
        for i in items:
            if i.checkState():
                checkListOn.append(i.data(QtCore.Qt.UserRole))
            else:
                checkListOff.append(i.data(QtCore.Qt.UserRole))

        indexList = paramIndexGet.GetString("IndexList")

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        toolList = None

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolList = group.GetString("ToolList")
            else:
                pass

        if toolList:
            toolList = toolList.split(".,.")
        else:
            toolList = []

        for i in checkListOn:
            if i not in toolList:
                toolList.append(i)
            else:
                pass

        for i in checkListOff:
            if i in toolList:
                toolList.remove(i)
            else:
                pass

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolList = group.SetString("ToolList", ".,.".join(toolList))
            else:
                pass

        buttonList()

    toolListWidget.itemChanged.connect(onToolListWidget)


    def buttonList2ToolList(buttonListWidget):

        items = []
        for index in range(buttonListWidget.count()):
            items.append(buttonListWidget.item(index))

        toolData = []
        for i in items:
            toolData.append(i.data(QtCore.Qt.UserRole))

        group = getGroup()
        group.SetString("ToolList", ".,.".join(toolData))


    buttonUp = QtGui.QToolButton()
    buttonUp.setIcon(QtGui.QIcon(iconUp))
    buttonUp.setToolTip("Move selected command up")
    buttonUp.setMinimumHeight(30)
    buttonUp.setMinimumWidth(30)


    def onButtonUp():
        currentIndex = buttonListWidget.currentRow()

        if currentIndex != 0:
            currentItem = buttonListWidget.takeItem(currentIndex)
            buttonListWidget.insertItem(currentIndex - 1, currentItem)
            buttonListWidget.setCurrentRow(currentIndex - 1)
            buttonList2ToolList(buttonListWidget)

    buttonUp.clicked.connect(onButtonUp)

    buttonDown = QtGui.QToolButton()
    buttonDown.setIcon(QtGui.QIcon(iconDown))
    buttonDown.setToolTip("Move selected command down")
    buttonDown.setMinimumHeight(30)
    buttonDown.setMinimumWidth(30)


    def onButtonDown():
        currentIndex = buttonListWidget.currentRow()

        if currentIndex != buttonListWidget.count() - 1 and currentIndex != -1:
            currentItem = buttonListWidget.takeItem(currentIndex)
            buttonListWidget.insertItem(currentIndex + 1, currentItem)
            buttonListWidget.setCurrentRow(currentIndex + 1)
            buttonList2ToolList(buttonListWidget)

    buttonDown.clicked.connect(onButtonDown)

    buttonRemoveCommand = QtGui.QPushButton()
    buttonRemoveCommand.setIcon(QtGui.QIcon(iconRemoveCommand))
    buttonRemoveCommand.setToolTip("Remove selected command")
    buttonRemoveCommand.setMinimumHeight(30)
    buttonRemoveCommand.setMinimumWidth(30)


    def onButtonRemoveCommand():

        currentIndex = buttonListWidget.currentRow()
        buttonListWidget.takeItem(currentIndex)

        if currentIndex != 0:
            buttonListWidget.setCurrentRow(currentIndex - 1)
        buttonListWidget.setFocus()
        buttonList2ToolList(buttonListWidget)
        toolList()

    buttonRemoveCommand.clicked.connect(onButtonRemoveCommand)

    vertexItem = QtGui.QTableWidgetItem()
    vertexItem.setText("Vertex")
    vertexItem.setToolTip("Set desired operator and vertex number")
    vertexItem.setFlags(QtCore.Qt.ItemIsEnabled)

    edgeItem = QtGui.QTableWidgetItem()
    edgeItem.setText("Edge")
    edgeItem.setToolTip("Set desired operator and edge number")
    edgeItem.setFlags(QtCore.Qt.ItemIsEnabled)

    faceItem = QtGui.QTableWidgetItem()
    faceItem.setText("Face")
    faceItem.setToolTip("Set desired operator and face number")
    faceItem.setFlags(QtCore.Qt.ItemIsEnabled)

    objectItem = QtGui.QTableWidgetItem()
    objectItem.setText("Object")
    objectItem.setToolTip("Set desired operator and object number")
    objectItem.setFlags(QtCore.Qt.ItemIsEnabled)


    def comboBox(TopoType):
        signList = ["<", "<=", "==", "!=", ">", ">="]

        model = QtGui.QStandardItemModel()

        for i in signList:
            item = QtGui.QStandardItem()
            item.setText(i)
            item.setData(TopoType, QtCore.Qt.UserRole)

            model.setItem(signList.index(i), 0, item)

        comboBoxSign = QtGui.QComboBox()
        comboBoxSign.setModel(model)
        comboBoxSign.setStyleSheet(styleCombo)

        def onCurrentIndexChanged():
            group = getGroup()

            groupContext = group.GetGroup("Context")
            text = comboBoxSign.currentText()
            topo = comboBoxSign.itemData(comboBoxSign.currentIndex(),
                                         QtCore.Qt.UserRole)
            groupContext.SetString(topo, text)

            contextList()

        comboBoxSign.currentIndexChanged.connect(onCurrentIndexChanged)

        return comboBoxSign

    vertexComboBox = comboBox("VertexSign")
    edgeComboBox = comboBox("EdgeSign")
    faceComboBox = comboBox("FaceSign")
    objectComboBox = comboBox("ObjectSign")


    def spinBox(TopoValue):

        spinBox = QtGui.QSpinBox()
        spinBox.setFrame(False)

        def onSpinBox():
            group = getGroup()

            groupContext = group.GetGroup("Context")
            value = spinBox.value()
            groupContext.SetInt(TopoValue, value)

            contextList()

        spinBox.valueChanged.connect(onSpinBox)

        return spinBox

    vertexSpin = spinBox("VertexValue")
    edgeSpin = spinBox("EdgeValue")
    faceSpin = spinBox("FaceValue")
    objectSpin = spinBox("ObjectValue")

    labelContext = QtGui.QLabel("Enable")
    checkContext = QtGui.QCheckBox()


    def setCheckContext():

        group = getGroup()
        groupContext = group.GetGroup("Context")

        if groupContext.GetBool("Enabled"):
            checkContext.setChecked(True)
            contextTable.setEnabled(True)
            resetButton.setEnabled(True)
        else:
            checkContext.setChecked(False)
            contextTable.setEnabled(False)
            resetButton.setEnabled(False)

        contextList()


    def onCheckContext():

        setDefaults()

        group = getGroup()
        groupContext = group.GetGroup("Context")

        if checkContext.isChecked():
            contextTable.setEnabled(True)
            resetButton.setEnabled(True)

            groupContext.SetBool("Enabled", 1)

        else:
            contextTable.setEnabled(False)
            resetButton.setEnabled(False)

            groupContext.SetBool("Enabled", 0)

        contextList()

    checkContext.stateChanged.connect(onCheckContext)

    contextTable = QtGui.QTableWidget(4, 3)
    contextTable.setMaximumHeight(120)
    contextTable.setFrameStyle(QtGui.QFrame.NoFrame)
    contextTable.verticalHeader().setVisible(False)
    contextTable.horizontalHeader().setVisible(False)
    try:
        contextTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        contextTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
    except AttributeError:
        contextTable.verticalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        contextTable.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)

    contextTable.setItem(0, 0, vertexItem)
    contextTable.setCellWidget(0, 1, vertexComboBox)
    contextTable.setCellWidget(0, 2, vertexSpin)

    contextTable.setItem(1, 0, edgeItem)
    contextTable.setCellWidget(1, 1, edgeComboBox)
    contextTable.setCellWidget(1, 2, edgeSpin)

    contextTable.setItem(2, 0, faceItem)
    contextTable.setCellWidget(2, 1, faceComboBox)
    contextTable.setCellWidget(2, 2, faceSpin)

    contextTable.setItem(3, 0, objectItem)
    contextTable.setCellWidget(3, 1, objectComboBox)
    contextTable.setCellWidget(3, 2, objectSpin)

    resetButton = QtGui.QToolButton()
    resetButton.setMinimumHeight(30)
    resetButton.setMinimumWidth(30)
    resetButton.setText(u'\u27F3')

    resetButton.setEnabled(False)


    def onResetButton():

        group = getGroup()
        group.RemGroup("Context")
        setDefaults()
        setCheckContext()

    resetButton.clicked.connect(onResetButton)


    def setDefaults():
        group = getGroup()
        groupContext = group.GetGroup("Context")

        vertexSign = groupContext.GetString("VertexSign")

        if vertexSign in sign:
            pass
        else:
            groupContext.SetString("VertexSign", "==")
            vertexSign = "=="

        for i in range(vertexComboBox.count()):
            if vertexComboBox.itemText(i) == vertexSign:
                vertexComboBox.setCurrentIndex(i)
            else:
                pass

        vertexValue = groupContext.GetInt("VertexValue")

        if vertexValue:
            pass
        else:
            a = groupContext.GetInt("VertexValue", True)
            b = groupContext.GetInt("VertexValue", False)

            if a == b:
                groupContext.SetInt("VertexValue", 0)
                vertexValue = 0
            else:
                groupContext.SetInt("VertexValue", 10)
                vertexValue = 10

        vertexSpin.setValue(vertexValue)

        edgeSign = groupContext.GetString("EdgeSign")

        if edgeSign in sign:
            pass
        else:
            groupContext.SetString("EdgeSign", "==")
            edgeSign = "=="

        for i in range(edgeComboBox.count()):
            if edgeComboBox.itemText(i) == edgeSign:
                edgeComboBox.setCurrentIndex(i)
            else:
                pass

        edgeValue = groupContext.GetInt("EdgeValue")

        if edgeValue:
            pass
        else:
            a = groupContext.GetInt("EdgeValue", True)
            b = groupContext.GetInt("EdgeValue", False)

            if a == b:
                groupContext.SetInt("EdgeValue", 0)
                edgeValue = 0
            else:
                groupContext.SetInt("EdgeValue", 10)
                edgeValue = 10

        edgeSpin.setValue(edgeValue)

        faceSign = groupContext.GetString("FaceSign")

        if faceSign in sign:
            pass
        else:
            groupContext.SetString("FaceSign", "==")
            faceSign = "=="

        for i in range(faceComboBox.count()):
            if faceComboBox.itemText(i) == faceSign:
                faceComboBox.setCurrentIndex(i)
            else:
                pass

        faceValue = groupContext.GetInt("FaceValue")

        if faceValue:
            pass
        else:
            a = groupContext.GetInt("FaceValue", True)
            b = groupContext.GetInt("FaceValue", False)

            if a == b:
                groupContext.SetInt("FaceValue", 0)
                faceValue = 0
            else:
                groupContext.SetInt("FaceValue", 10)
                faceValue = 10

        faceSpin.setValue(faceValue)

        objectSign = groupContext.GetString("ObjectSign")

        if objectSign in sign:
            pass
        else:
            groupContext.SetString("ObjectSign", "==")
            objectSign = "=="

        for i in range(objectComboBox.count()):
            if objectComboBox.itemText(i) == objectSign:
                objectComboBox.setCurrentIndex(i)
            else:
                pass

        objectValue = groupContext.GetInt("ObjectValue")

        if objectValue:
            pass
        else:
            a = groupContext.GetInt("ObjectValue", True)
            b = groupContext.GetInt("ObjectValue", False)

            if a == b:
                groupContext.SetInt("ObjectValue", 0)
                objectValue = 0
            else:
                groupContext.SetInt("ObjectValue", 10)
                objectValue = 10

        objectSpin.setValue(objectValue)

        valueRadius = group.GetInt("Radius")

        if valueRadius:
            pass
        else:
            valueRadius = 100
            group.SetInt("Radius", valueRadius)

        spinRadius.setValue(valueRadius)

        valueButton = group.GetInt("Button")

        if valueButton:
            pass
        else:
            valueButton = 32
            group.SetInt("Button", valueButton)

        spinButton.setValue(valueButton)

        contextList()


    def setDefaultPie(restore=False):
        paramGet = App.ParamGet("User parameter:BaseApp/PieMenu")
        paramIndexGet = App.ParamGet("User parameter:BaseApp/PieMenu/Index")
        indexList = paramIndexGet.GetString("IndexList")

        defaultTools = ["Std_ViewTop",
                        "Std_New",
                        "Std_ViewRight",
                        "Std_BoxSelection",
                        "Std_ViewBottom",
                        "Std_ViewIsometric",
                        "Std_ViewLeft",
                        "Std_ViewScreenShot"]

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        if 0 in indexList:
            if restore:
                group = paramIndexGet.GetGroup("0")
                group.SetString("ToolList", ".,.".join(defaultTools))                
            else:
                pass
        else:
            indexList.append(0)

            temp = []

            for i in indexList:
                temp.append(str(i))

            indexList = temp

            paramIndexGet.SetString("0", "Default")
            paramIndexGet.SetString("IndexList", ".,.".join(indexList))

            group = paramIndexGet.GetGroup("0")
            group.SetString("ToolList", ".,.".join(defaultTools))

        paramGet.SetBool("ToolBar", False)
        paramGet.RemString("ToolBar")
        paramGet.SetString("CurrentPie", "Default")

        group = getGroup(mode=1)

        group.SetInt("Radius", 100)
        group.SetInt("Button", 32)

    def onTriggerSequenceChanged(seq):
        seqAsString = seq.toString()

        if len(seqAsString) == 0:
            return

        singleSequence = seqAsString.split(', ')[-1]

        keySequenceEdit.setKeySequence(singleSequence)
        App.ParamGet("User parameter:BaseApp/PieMenu").SetString("triggerShortcut", singleSequence)

        if actionKey:
            actionKey.setShortcut(keySequenceEdit.keySequence())

    keySequenceEdit = QtGui.QKeySequenceEdit()
    keySequenceEdit.setKeySequence(App.ParamGet("User parameter:BaseApp/PieMenu").GetString("triggerShortcut") or "TAB")
    keySequenceEdit.keySequenceChanged.connect(onTriggerSequenceChanged)

    keySequenceLabel = QtGui.QLabel("Trigger shortcut")

    def onControl():

        global pieMenuDialog

        for i in mw.findChildren(QtGui.QDialog):
            if i.objectName() == "PieMenuPreferences":
                i.deleteLater()
            else:
                pass

        tabs = QtGui.QTabWidget()

        pieMenuTab = QtGui.QWidget()
        pieMenuTabLayout = QtGui.QVBoxLayout()
        pieMenuTab.setLayout(pieMenuTabLayout)

        layoutKeySequenceEdit = QtGui.QHBoxLayout()
        layoutKeySequenceEdit.addWidget(keySequenceLabel)
        layoutKeySequenceEdit.addStretch(1)
        layoutKeySequenceEdit.addWidget(keySequenceEdit)

        layoutAddRemove = QtGui.QHBoxLayout()
        layoutAddRemove.addWidget(cBox)
        layoutAddRemove.addWidget(buttonAddPieMenu)
        layoutAddRemove.addWidget(buttonRemovePieMenu)
        layoutAddRemove.addWidget(buttonRenamePieMenu)
        layoutAddRemove.addWidget(buttonCopyPieMenu)

        layoutRadius = QtGui.QHBoxLayout()
        layoutRadius.addWidget(labelRadius)
        layoutRadius.addStretch(1)
        layoutRadius.addWidget(spinRadius)

        layoutButton = QtGui.QHBoxLayout()
        layoutButton.addWidget(labelButton)
        layoutButton.addStretch(1)
        layoutButton.addWidget(spinButton)

        pieMenuTabLayout.insertLayout(0, layoutKeySequenceEdit)
        pieMenuTabLayout.insertLayout(1, layoutAddRemove)
        pieMenuTabLayout.insertSpacing(2, 24)
        pieMenuTabLayout.insertLayout(3, layoutRadius)
        pieMenuTabLayout.insertLayout(4, layoutButton)
        pieMenuTabLayout.addStretch(0)

        contextTab = QtGui.QWidget()
        contextTabLayout = QtGui.QVBoxLayout()
        contextTab.setLayout(contextTabLayout)

        layoutCheckContext = QtGui.QHBoxLayout()
        layoutCheckContext.addWidget(labelContext)
        layoutCheckContext.addStretch(1)
        layoutCheckContext.addWidget(checkContext)

        resetLayout = QtGui.QHBoxLayout()
        resetLayout.addStretch(1)
        resetLayout.addWidget(resetButton)

        contextTabLayout.insertLayout(0, layoutCheckContext)
        contextTabLayout.addWidget(contextTable)
        contextTabLayout.insertLayout(2, resetLayout)
        contextTabLayout.addStretch(1)

        tabs.addTab(pieMenuTab, "PieMenu")
        tabs.addTab(toolListWidget, "Tools")
        tabs.addTab(contextTab, "Context")

        pieButtons = QtGui.QWidget()
        pieButtonsLayout = QtGui.QVBoxLayout()
        pieButtons.setLayout(pieButtonsLayout)
        pieButtonsLayout.setContentsMargins(0, 0, 0, 0)
        pieButtonsLayout.addWidget(buttonListWidget)

        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(buttonRemoveCommand)
        buttonsLayout.addWidget(buttonDown)
        buttonsLayout.addWidget(buttonUp)

        pieButtonsLayout.insertLayout(1, buttonsLayout)

        vSplitter = QtGui.QSplitter()
        vSplitter.insertWidget(0, pieButtons)
        vSplitter.insertWidget(0, tabs)

        preferencesWidget = QtGui.QWidget()
        preferencesLayout = QtGui.QHBoxLayout()
        preferencesLayout.setContentsMargins(0, 0, 0, 0)
        preferencesWidget.setLayout(preferencesLayout)
        preferencesLayout.addWidget(vSplitter)

        pieMenuDialog = QtGui.QDialog(mw)
        pieMenuDialog.resize(800, 450)
        pieMenuDialog.setObjectName("PieMenuPreferences")
        pieMenuDialog.setWindowTitle("PieMenu " + PIE_MENU_VERSION)
        pieMenuDialogLayout = QtGui.QVBoxLayout()
        pieMenuDialog.setLayout(pieMenuDialogLayout)
        pieMenuDialog.show()

        pieMenuDialogLayout.addWidget(preferencesWidget)

        cBoxUpdate()


    def addAccessoriesMenu():

        if mw.property("eventLoop"):

            startAM = False
            try:
                mw.mainWindowClosed
                mw.workbenchActivated
                startAM = True
            except AttributeError:
                pass
            if startAM:
                t.stop()
                t.deleteLater()
                accessoriesMenu()


    mw = Gui.getMainWindow()
    actionKey = None
    start = True

    for action in mw.findChildren(QtGui.QAction):
        if action.objectName() == "PieMenuShortCut":
            start = False
        else:
            pass

    if start:

        remObsoleteParams()
        compositingManager = True
        if QtCore.qVersion() < "5":
            windowShadow = False
        else:
            windowShadow = True

        if platform.system() == "Linux":
            try:
                if QtGui.QX11Info.isCompositingManagerRunning():
                    windowShadow = True
                else:
                    compositingManager = False
            except AttributeError:
                windowShadow = True
        else:
            pass

        if platform.system() == "Windows":
            windowShadow = True
        else:
            pass

        contextAll = {}
        contextList()
        selObserver = SelObserver()
        addObserver()

        PieMenuInstance = PieMenu()

        actionKey = QtGui.QAction(mw)
        actionKey.setText("Invoke pie menu")
        actionKey.setObjectName("PieMenuShortCut")
        actionKey.setShortcut(keySequenceEdit.keySequence())
        actionKey.triggered.connect(PieMenuInstance.showAtMouse)
        mw.addAction(actionKey)

        # let the addition of the accessoriesMenu wait until FC is ready for it
        t = QtCore.QTimer()
        t.timeout.connect(addAccessoriesMenu)
        t.start(500)

    else:
        pass

pieMenuStart()