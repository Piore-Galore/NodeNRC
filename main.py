import yaml
import os, sys, inspect
from qtpy.QtWidgets import QApplication

from nodeeditor.utils import loadStylesheet
from nodeeditor.node_editor_window import NodeEditorWindow
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_node import Node
import os.path as path
import document.excel_sheet as sheet
import document.excel_row as row
import document.field_descriptor as descriptor 

def DialogueNodes(Scene):
    with open(path.abspath("DIALOGUE_CONF.yaml"), "rb") as stream:
        try:
            Yam = yaml.unsafe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    if Yam:
        Xpos = 0
        Ypos = 0
        for field in Yam.body:
            TmpNode = Node(Scene, "")
            TmpNode.setPos(Xpos,Ypos)
            Xpos = Xpos + 300
            if Xpos >= 2100:
                Ypos = Ypos + 300
                Xpos = 0 
            for key in field.data.keys():
                TmpNode
    
def main():
    app = QApplication(sys.argv)

    Window = NodeEditorWindow()
    #Window.nodeeditor.addNodes()

    CurrentScene = Window.nodeeditor.scene
    DialogueNodes(CurrentScene)

    loadStylesheet(path.abspath('Style/nodeeditor-dark.qss'))

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()