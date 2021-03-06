import os
from pathlib import Path
from PIL import Image


def get_cords(pattern_id, slogosize, background_size):
    # Takes pattern and returns a list of tuples for where to
    # paste sized logo on background pic or template. Unit is pixels
    cord_list = []
    composite_list = []

    small_X = slogosize[0]
    small_halfX = int(small_X/2)
    small_Y = slogosize[1]
    small_halfY = int(small_Y/2)

    b_X = background_size[0]
    b_halfX = int(b_X/2)
    b_Y = background_size[1]
    b_halfY = int(b_Y/2)

    if pattern_id == 'Top-Left':
        cord_list = [(0, 0)]
    elif pattern_id == 'Top-Middle':
        cord_list = [((b_halfX-small_halfX), 0)]
    elif pattern_id == 'Top-Right':
        cord_list = [((b_X-small_X), 0)]
    elif pattern_id == 'Center-Left':
        cord_list = [(0, (b_halfY-small_halfY))]
    elif pattern_id in ['Center', 'Center-MAX', 'Center-HALF']:
        cord_list = [((b_halfX-small_halfX), (b_halfY-small_halfY))]
    elif pattern_id == 'Center-Right':
        cord_list = [((b_X-small_X), (b_halfY-small_halfY))]
    elif pattern_id == 'Bottom-Left':
        cord_list = [(0, (b_Y-small_Y))]
    elif pattern_id == 'Bottom-Middle':
        cord_list = [((b_halfX-small_halfX), (b_Y-small_Y))]
    elif pattern_id == 'Bottom-Right':
        cord_list = [((b_X-small_X), (b_Y-small_Y))]
    elif pattern_id == '3x3ring':
        # uses all alignments except center
        composite_list = (['Top-Left', 'Top-Middle', 'Top-Right',
                           'Center-Left', 'Center-Right', 'Bottom-Left',
                           'Bottom-Middle', 'Bottom-Right'])
        for item in composite_list:
            cord_list.extend(get_cords(item, slogosize, background_size))
    elif pattern_id == '3x3full':
        # This 3x3 is all locations + center
        composite_list = ['3x3ring', 'Center']
        for item in composite_list:
            cord_list.extend(get_cords(item, slogosize, background_size))
    elif pattern_id == 'Corners':
        composite_list = (['Top-Left', 'Top-Right',
                           'Bottom-Left', 'Bottom-Right'])
        for item in composite_list:
            cord_list.extend(get_cords(item, slogosize, background_size))
    elif pattern_id == '4x4full':

        x_list = ([0, int(small_X + (b_X-4*small_X)/3),
                  int(b_X-2*small_X - (b_X-4*small_X)/3), b_X-small_X])
        y_list = ([0, int(small_Y + (b_Y-4*small_Y)/3),
                  int(b_Y-2*small_Y - (b_Y-4*small_Y)/3), b_Y-small_Y])

        for x in x_list:
            for y in y_list:
                cord_list.append((x, y))

    elif pattern_id == '4x4ring':
        # Top-Bottom Rows
        x_list = ([0, int(small_X + (b_X-4*small_X)/3),
                  int(b_X-2*small_X - (b_X-4*small_X)/3), b_X-small_X])
        y_list = ([0, b_Y-small_Y])

        for x in x_list:
            for y in y_list:
                cord_list.append((x, y))

        # Middle Two Rows
        x_list = ([0, b_X-small_X])
        y_list = ([int(small_Y + (b_Y-4*small_Y)/3),
                  int(b_Y-2*small_Y - (b_Y-4*small_Y)/3)])

        for x in x_list:
            for y in y_list:
                cord_list.append((x, y))

    return cord_list


def final_background(logo, output_size, pattern, force_ratio=-1):
    # logo (image), output_size (tuple), pattern (pattern_id)
    # returns final_background of white with logos pasted
    # onto it based on the patter chosen

    # Calculate slogo size based on ratio between logo and ouput_size
    # Resize logo image as slogo

    ratioX = output_size[0]/logo.size[0]
    ratioY = output_size[1]/logo.size[1]

    # Min taken so small logo pasted will fit in final pic
    resizeratio = min(ratioX, ratioY)

    # Resize logo to pasting size use pattern_dic if no force_ratio
    if force_ratio != -1:
        resizeratio = resizeratio*force_ratio
    else:
        resizeratio = resizeratio*pattern_dic[pattern]

    logo = logo.resize((int(logo.size[0]*resizeratio),
                        int(logo.size[1]*resizeratio)))

    # Create a full sized white image to paste small logo images on
    whitepic = Image.new('RGBA', output_size, 0)

    paste_array = get_cords(pattern, logo.size, output_size)

    for location in paste_array:
        whitepic.paste(logo, location)

    return whitepic


def make_transparent(im, alpha_value=50):
    '''
    Take image im and makes white or near white pixels transparent
    alpha_value optional transparency of non-white pixles
    '''
    image = im

    # NON-RGBA image types needs conversion to add alpha values
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Transparency
    newImage = []
    for item in image.getdata():
        # making 'near white' pixels transparent
        if item[0] >= 220:
            newImage.append((255, 255, 255, 0))
        else:
            newImage.append((item[0], item[1], item[2], alpha_value))

    image.putdata(newImage)

    return image


def populate_filenames(f_dic, dir_list, allowed):
    '''
    f_dic : dictionary where key is string directory name
    dir_list : string list of required directories (at cwd level)
    allowed : string list of compatible file extensions
    '''
    for folder_name in dir_list:
        folder_path = os.path.join(base_path, folder_name)
        f_dic[folder_name] = []

        # Adds filenames to file_dic if file extention is in [image_types]
        for f in filter(lambda f: f.split('.')[1] in allowed,
                        os.listdir(folder_path)):
            f_dic[folder_name].append(f)


def get_files(f_dic, dir_list, allowed):
    '''
    This function checks the prerequisite folders exist, creating them
    if missing.
    '''

    complete = True

    existing_folders = os.listdir(base_path)

    # Check that all required folders exist
    if all(item in existing_folders for item in dir_list) is False:

        # Create missing folders
        missing = list(set(dir_list)-set(existing_folders))
        print(f'We are missing these folders {missing}')
        for item in missing:
            print(f'Creating a folder named {item}')
            os.makedirs(os.path.join(base_path, item))

    populate_filenames(f_dic, dir_list, allowed)


def select_from_list(my_list, description='Enter the item number '):
    '''
    Returns value of the item the user selects
    If there is only one item it is chosen
    'CANCEL' is returned if user cancels, 'EMPTY' if the list is empty
    List items displayed in two columns if more than 5 items
    '''

    choice = ''
    length = len(my_list)

    if length == 0:
        return 'EMPTY'
    elif length == 1:
        return my_list[0]
    else:
        if length > 5:
            # Two Column Output
            temp_row = ''
            rows = int(length/2+0.5)
            for row_num in range(rows):
                temp_row = (f'({row_num + 1:02}) {my_list[row_num]}').ljust(30)
                # add second column if there is one
                if row_num + rows < length:
                    temp_row = (temp_row + f'({row_num + rows + 1:02}) ' +
                                f'{my_list[row_num + rows]}').ljust(30)
                print(temp_row)
        else:
            for index, item in enumerate(my_list):
                print(f'({index+1:02}) {item}')

        while choice not in range(length+1):
            try:
                print(f'{description} (0 to cancel)', end=' ')
                choice = int(input())
            except:
                continue
        if choice == 0:
            return 'CANCEL'
    return (my_list[choice-1])


def output_pic(im, im_name, folder_name, show=False, save=False, wall=False):
    '''
    This takes in image, im_name (str) and a folder_name (str)

    save (optional) saves file in the folder_name
    The image is saved adding -w in the folder_name
    This folder is in same dir level as this program

    show (optional) displays output file using default program
    wall (optional) wallpaper images output as .png
    '''
    name_parts = im_name.split('.')

    if wall:
        new_name = name_parts[0] + '-w.png'
    else:
        new_name = name_parts[0] + '-m.' + name_parts[1]

    f_path = base_path.joinpath(folder_name, new_name)

    if show:
        im.show()
    if save:
        print(f'Saving File :\t{f_path}')
        im.save(f_path)


def process_pictures(pattern='Top-Left', show=False, save=True, lalpha=50,
                     fr=-1, wall=False):
    RGBmode = False
    if show:
        print(f'Displaying {len(file_dic[source_folder_name])} '
              f'merged image(s) using your default program.')
    if save is True:
        print(f'SAVING {len(file_dic[source_folder_name])} '
              f'merged image(s) in folder "finishedpics"')
        if wall:
            print(f'SAVING Wallpaper Image in folder "finishedpics"')

    # process original logo to get transparent logo
    logo_path = base_path.joinpath(logo_folder_name, source_logo)
    logo = Image.open(logo_path)
    logo = make_transparent(logo, lalpha)

    for item in file_dic[source_folder_name]:
        RGBmode = False
        orig_path = base_path.joinpath(source_folder_name, item)
        orig_pic = Image.open(orig_path)

        if orig_pic.mode in ['RGB', 'P', '1', 'L']:
            RGBmode = True
            orig_pic = orig_pic.convert("RGBA")

        logo_sheet = final_background(logo, orig_pic.size, pattern,
                                      force_ratio=user_options[5])

        final_pic = Image.alpha_composite(orig_pic, logo_sheet)

        if RGBmode:
            final_pic = final_pic.convert('RGB')

        output_pic(final_pic, item, 'finishedpics', show, save)

    # process Wallpaper if selected (960,540) size is default
    if wall:
        wallimage = final_background(logo, (960, 540), pattern,
                                     force_ratio=user_options[5])
        output_pic(wallimage, source_logo, 'finishedpics', show, save,
                   wall=True)


def construct_pattern_dic():
    # Creates pattern dictionary and assigned default logo ratios
    temp = {}
    key_list = (['Top-Left', 'Top-Middle', 'Top-Right', 'Center-Left',
                 'Center', 'Center-Right', 'Bottom-Left', 'Bottom-Middle',
                 'Bottom-Right', '3x3full', '3x3ring', 'Center-MAX',
                 'Center-HALF', 'Corners', '4x4full', '4x4ring'])

    for item in key_list:
        if 'MAX' in item:
            temp[item] = 1
        elif 'HALF' in item:
            temp[item] = 0.5
        elif '4x4' in item:
            temp[item] = 0.25
        elif 'Top-Left' in item:
            temp[item] = 0.25
        else:
            temp[item] = 0.33

    return temp


def get_user_options(options):
    # pattern,logoalpha,wallpaper,display,save,forcesize
    # This function gets user input and changes program options

    choice = ''
    temp = ''
    option_cats = (['RESTORE DEFAULT VALUES', 'Logo Pattern', 'Output Mode',
                    'Wallpaper', 'LogoAlphaValue (Advanced)',
                    'ForceLogoRatio (Advanced)'])
    output_options = (['DISPLAY ONLY', 'SAVE ONLY', 'SAVE AND DISPLAY',
                       'NO OUTPUT'])
    finished = False

    if len(options) == 0:
        options = default_options.copy()

    while finished is False:

        os.system('cls' if os.name == 'nt' else 'clear')

        if options[4] and options[3]:
            temp = output_options[2]
        elif options[4]:
            temp = output_options[1]
        elif options[3]:
            temp = output_options[0]
        else:
            temp = output_options[3]

        print('==== CURRENT SETTINGS ====')
        print(f'Logo Chosen : {source_logo:20}Number of files in '
              f'{source_folder_name} : {len(file_dic[source_folder_name])}\n')
        print(f'Pattern     : {options[0]:20}Output           : {temp}')
        print(f'Wallpaper   : {options[2]}\t\t  Advanced Options : ', end="")
        if options[1] == default_options[1] and (
           options[5] == default_options[5]):
            print('standard')
        else:
            print('CUSTOM')
        print('==========================')

        # EDIT OPTIONS?
        try:
            choice = input('EDIT OPTIONS? ')
            if choice[0].lower() == 'y':
                # User selections option to change
                choice = select_from_list(option_cats,
                                          'Select Option to Edit : ')
                if choice not in ['EMPTY', 'CANCEL']:
                    if choice == option_cats[0]:
                        options = default_options.copy()
                        print(options, default_options)
                    elif choice == 'Logo Pattern':
                        choice = select_from_list(list(pattern_dic.keys()),
                                                  'Select Pattern')
                        if not (choice == 'EMPTY' or choice == 'CANCEL'):
                            options[0] = choice
                    elif choice == option_cats[2]:
                        choice = select_from_list(output_options,
                                                  'Select Output Option')
                        if not (choice == 'EMPTY' or choice == 'CANCEL'):
                            if choice == output_options[0]:    # 'DISPLAY ONLY'
                                options[3] = True
                                options[4] = False
                            elif choice == output_options[1]:  # SAVE ONLY
                                options[3] = False
                                options[4] = True
                            elif choice == output_options[2]:  # SAVE + DISPLAY
                                options[3] = True
                                options[4] = True
                            else:                              # NO OUTPUT
                                options[3] = False
                                options[4] = False
                    elif choice == option_cats[3]:
                        print(choice)
                        choice = input('Enter Yes for Wallpaper (Logo on white'
                                       ' background only) : ')
                        if choice != '':
                            if choice[0].lower() == 'y':
                                options[2] = True
                            else:
                                options[2] = False
                    elif choice == option_cats[4]:
                        print(choice)
                        print(f'Transparency of Logo before merging '
                              f'{options[1]/25.5: .1f}')

                        # adjust alpha component of logo in make_transparent()
                        try:
                            print('Enter value 1 to 10 (very light 1 --> 10'
                                  ' opaque) :')
                            choice = float(input(' '))
                            if (choice >= 0 and choice <= 10):
                                options[1] = int(choice*25.5)
                        except:
                            options[1] = default_options[1]
                    elif choice == option_cats[5]:
                        print(choice + '\nThis option replaces the default '
                              'logo size ratio with respect to the picture '
                              'being merged with\nThis value is usually'
                              'dependent on the pattern chosen.')
                        print("Enter a value of 10-100: ", end='')
                        try:
                            choice = float(input('100 is forcing logo ' +
                                                 'to max size : '))
                            if (choice >= 10 and choice <= 100):
                                options[5] = choice/100
                        except:
                            options[5] = default_options[5]
            else:
                finished = True
        except:
            finished = True

    return options


def choose_logo():
    '''
    Allows user to select desired logo image
    If only one it is chosen automatically
    Uses a filepath of current + logo_folder_name (global)
    Returns the filename of the image selected, 'CANCEL' or 'EMPTY'
    '''

    temp = ''
    done = False
    while not done:
        # populate file dictionary for all folders
        populate_filenames(file_dic, folders_required, image_types)

        source_logo = select_from_list(file_dic[logo_folder_name],
                                       'Choose a logo ')

        if len(file_dic[logo_folder_name]) == 1:
            print (source_logo + ' chosen automatically because there is only'
                                 ' one compatible image in logo folder.')
            done = True

        if source_logo == 'EMPTY':
            print('There are 0 files in your logo folder. It is required that '
                  'you have at least one logo image of a compatible filetype.')
            print(f'Compatible filetypes are : {image_types}')
            print(f'The folder to store logos is located at '
                  f'{os.path.join(base_path, logo_folder_name)}')
            choice = input('Would you like to re-try?')
            try:
                if choice[0].lower() != 'y':
                    done = True
                else:
                    done = False
            except:
                done = True

        elif source_logo == 'CANCEL':
            try:
                choice = input('You have not chosen a logo. '
                               'Are you sure you want to EXIT? ')
                if choice[0].lower() != 'n':
                    done = True
            except:
                done = True
        else:
            done = True

    return source_logo

# MAiN
base_path = Path.cwd()
folders_required = ['logos', 'originalpics', 'finishedpics']
image_types = ['jpg', 'png', 'bmp', 'gif']
file_dic = {}
default_options = ['Top-Left', 50, False, False, True, -1]
user_options = []
choice = ''

pattern_dic = construct_pattern_dic()

source_logo = ''
keep_going = True

# Must be an element of [folders_required]
source_folder_name = 'originalpics'
logo_folder_name = 'logos'

# MAIN
while keep_going:
    get_files(file_dic, folders_required, image_types)
    source_logo = choose_logo()
    if source_logo in ['EMPTY', 'CANCEL']:
        keep_going = False
    else:
        user_options = get_user_options(user_options)

        # Verify User Continue if 0 files in 'originalpics'
        if (len(file_dic[source_folder_name]) != 0 or
           user_options[2] is True):

            process_pictures(pattern=user_options[0], show=user_options[3],
                             save=user_options[4], lalpha=user_options[1],
                             fr=user_options[5], wall=user_options[2])

        else:
            print(f'You have no images to process in {source_folder_name}')

        choice = input('Make more images? ')
        try:
            if choice[0].lower() == 'y':
                keep_going = True
            else:
                keep_going = False
        except:
            keep_going = False

print('PROGRAM TERMINATED')
