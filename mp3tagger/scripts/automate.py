from subprocess import Popen
from pywinauto import Desktop
from pywinauto.application import Application
# import pywinauto
import os

def automate(filter):

    # FASTER BUT CAN'T FIND SCORE TOTAL
    try:
        # connect again with this faster way to find the filter
        app = Application().connect(path=os.environ.get("MP3TAG_PATH"))
    except:
        print('are you sure mp3 tag is open before you connect?')
        exit()

    window =  app.top_window()
    

    window.maximize()
    # print(dlg_spec.menu())

    # #  TAKES A LOOOOOOOOOOOONG TIME IF THERE ARE MANY SONGS IN THE VIEW
    # window.print_control_identifiers()

    # sys.exit()

    # filter.replace( '(' ,  r'\(' )
    filter = filter.replace( ')' ,  '{)}')
    filter = filter.replace( '(' ,  '{(}')
    filter = filter.replace( ' ' ,  '{ }')
    filter = filter.replace( '%' ,  '{%}')

    # filter = filter[3:5]
    print(filter)
    # https://stackoverflow.com/questions/44369703/attributeerror-windowspecification-class-has-no-typekeys-method


    # # add the filter text to the filter
    # window.child_window(best_match="ComboBox").type_keys(filter)

    # FOR NOT BACKEND = UAI
    window['Filte&r:ComboBox'].type_keys(filter)

    

    # window['Filte&r:ComboBox'].send_message(filter)

    # window['Filte&r:ComboBox'].type_keys('')
    # filter = filter.replace('{','').replace('}', '')
    # chars = [c for c in filter if not c == '(' and not c == ')']
    # chars = [c for c in filter if not c == '{' and not c == '}']
    # print(chars)
    # # chars = ['{', '(', '}', '{', '(', '}', 'N', 'O', 'T', '{', ' ', '}', 'B', 'P', 'M', '{', ' ', '}', 'L', 'E', 'S', 'S', '{', ' ', '}', '8', '0', '{', ' ', '}', 'A', 'N', 'D', '{', ' ', '}', 'N', 'O', 'T', '{', ' ', '}', 'B', 'P', 'M', '{', ' ', '}', 'G', 'R', 'E', 'A', 'T', 'E', 'R', '{', ' ', '}', '1', '0', '0', '{', ')', '}', '{', ' ', '}', 'O', 'R', '{', ' ', '}', '{', '(', '}', 'N', 'O', 'T', '{', ' ', '}', 'B', 'P', 'M', '{', ' ', '}', 'L', 'E', 'S', 'S', '{', ' ', '}', '1', '6', '0', '{', ' ', '}', 'A', 'N', 'D', '{', ' ', '}', 'N', 'O', 'T', '{', ' ', '}'
    
    # window['Filte&r:ComboBox'].send_chars(chars, with_spaces=True)



# Popen(r'os.environ.get("MP3TAG_PATH")', shell=True)
    
    
    # dlg = Desktop(backend="uia").mp3tag
    # dlg.wait('visible')
    
    # app = Application().start(r'os.environ.get("MP3TAG_PATH")')


    # # CONNECT AGAIN WITH THIS SLOWER BACK END THAT FIND'S THE SCORETOTAL. THIS ONE FAILS CUZ IT'S TOO SLOW IF MANY SONGS IN WINDOW
    # try:
    #     app = Application(backend="uia").connect(path=r'os.environ.get("MP3TAG_PATH")')
    # except:
    #     print('are you sure mp3 tag is open before you connect?')
    #     sys.exit()

    # # sort by scoreTotal
    # # window.scoreTotal.print_control_identifiers()
    # window.child_window(title="scoreTotal", auto_id="HeaderItem 1", control_type="HeaderItem").click_input()

    # app.Properties.print_control_identifiers()
    # sleep(3)
    # dialogs = app.windows()
    # pprint(dialogs)
    # sys.exit()