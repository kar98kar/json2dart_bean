import json

import pyperclip
import wx

APP_TITLE = u'Dart生成'


class MainFrame(wx.Frame):
    """程序主窗口类，继承自wx.Frame"""

    base_bean = """
abstract class BaseBean {

  BaseBean();
  
  BaseBean.fromJson(String json) {
    var action = jsonDecode(json);
    _initBean(action);
  }

   BaseBean _initBean(Map map);
}
"""

    bean_format = """
class %s extends BaseBean {
  %s

  %s();

  @override
  %s _initBean(Map map) {
    %s
    return this;
  }
}
"""

    field_normal_format = "%s %s;"

    field_list_format = "List<%s> %s;"

    assignment_normal_format = "%s = map['%s'];"

    assignment_list_format = "%s = map['%s']?.map<%s>((item) => %s()._initBean(item))?.toList();"

    assignment_bean_format = "%s = %s()._initBean(map['%s']);"

    def __init__(self):
        """构造函数"""

        wx.Frame.__init__(self, None, -1, APP_TITLE, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        # 默认style是下列项的组合：wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU |
        # wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN

        self.SetBackgroundColour(wx.Colour(224, 224, 224))
        self.SetSize((800, 630))
        self.Center()

        wx.StaticText(self, -1, u'类名：', pos=(8, 14), size=(40, -1), style=wx.ALIGN_LEFT)
        self.class_name = wx.TextCtrl(self, -1, '', pos=(50, 10), size=(200, -1), name='TC02',
                                      style=wx.ALIGN_LEFT)
        wx.StaticText(self, -1, u'Json：', pos=(8, 44), size=(40, -1), style=wx.ALIGN_LEFT)
        self.json = wx.TextCtrl(self, -1, '', pos=(8, 70), size=(768, 220), name='TC01',
                                style=wx.ALIGN_LEFT | wx.TE_MULTILINE | wx.TE_RICH2)
        wx.StaticText(self, -1, u'结果：', pos=(8, 298), size=(100, -1), style=wx.ALIGN_LEFT)
        self.result = wx.TextCtrl(self, -1, '', pos=(8, 320), size=(768, 220), name='TC01',
                                  style=wx.ALIGN_LEFT | wx.TE_MULTILINE | wx.TE_RICH2)

        self.btn_gen = wx.Button(self, -1, u'生成代码', pos=(676, 550), size=(100, 25))
        self.btn_clear = wx.Button(self, -1, u'清空', pos=(566, 550), size=(100, 25))
        self.btn_format = wx.Button(self, -1, u'格式化Json', pos=(676, 293), size=(100, 25))
        self.btn_copy_base_class = wx.Button(self, -1, u'复制基类', pos=(566, 293), size=(100, 25))

        self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear)
        self.btn_format.Bind(wx.EVT_BUTTON, self.on_format)
        self.btn_gen.Bind(wx.EVT_BUTTON, self.on_gen)
        self.btn_copy_base_class.Bind(wx.EVT_BUTTON, self.on_copy_base_class)

    def on_copy_base_class(self, evt):
        pyperclip.copy(self.base_bean)
        wx.MessageBox('已复制到剪切板', 'Info', wx.OK | wx.ICON_INFORMATION)

    def on_clear(self, evt):
        self.class_name.Clear()
        self.json.Clear()

    def on_format(self, evt):
        try:
            json_str = self.json.GetValue()
            json_obj = json.loads(json_str)
            self.json.SetValue(json.dumps(json_obj, indent=4))
        except Exception as e:
            pass

    def on_gen(self, evt):
        try:
            self.on_format(None)
            class_name = self.class_name.GetValue()
            json_str = self.json.GetValue()
            json_obj = json.loads(json_str)
            codes = self.code_gen(class_name, json_obj)
            codes.reverse()
            self.result.SetValue(''.join(codes))
            pyperclip.copy(''.join(codes))
            wx.MessageBox('已复制到剪切板', 'Info', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            pass

    def gen_class_code(self, class_name, fields, assignments):
        return self.bean_format % (class_name, '\n  '.join(fields), class_name,
                                   class_name, '\n    '.join(assignments))

    def code_gen(self, class_name, json_obj):
        fields = []
        assignments = []
        codes = []
        for key, value in json_obj.items():
            if type(value) == int:
                fields.append(self.field_normal_format % ('int', key))
                assignments.append(self.assignment_normal_format % (key, key))
            elif type(value) == str:
                fields.append(self.field_normal_format % ('String', key))
                assignments.append(self.assignment_normal_format % (key, key))
            elif type(value) == float:
                fields.append(self.field_normal_format % ('Double', key))
                assignments.append(self.assignment_normal_format % (key, key))
            elif type(value) == list:
                if len(value) > 0:
                    name = "%sBean" % key
                    names = []
                    for index in range(len(name)):
                        if index == 0:
                            names.append(name[index].upper())
                        else:
                            names.append(name[index])
                    name = ''.join(names)
                    codes += self.code_gen(name, value[0])
                    fields.append(self.field_list_format % (name, key))
                    assignments.append(self.assignment_list_format % (key, key, name, name))
            elif type(value) == dict:
                name = "%sBean" % key
                names = []
                for index in range(len(name)):
                    if index == 0:
                        names.append(name[index].upper())
                    else:
                        names.append(name[index])
                name = ''.join(names)
                codes += self.code_gen(name, value)
                fields.append(self.field_normal_format % (name, key))
                assignments.append(self.assignment_bean_format % (key, name, key))
        codes.append(self.gen_class_code(class_name, fields, assignments))
        return codes


class MainApp(wx.App):
    frame = None

    def OnInit(self):
        self.SetAppName(APP_TITLE)
        self.frame = MainFrame()
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MainApp(redirect=True)
    app.MainLoop()
