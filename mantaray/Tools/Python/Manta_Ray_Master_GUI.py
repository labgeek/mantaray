#!/usr/bin/env python3
# This program is the master GUI for the Manta Ray project.
# version 1.16

"""
Version Update:

+1.16 - CBryce
    Added GA Parser and Batch Mode

+1.15 - KMurphy
    Created by Kevin Murphy

"""

##########################COPYRIGHT INFORMATION############################
# Copyright (C) 2014 Kevin.Murphy@mantech.com        					  #
# This program is free software: you can redistribute it and/or modify    #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# This program is distributed in the hope that it will be useful,         #
# but WITHOUT ANY WARRANTY; without even the implied warranty of          #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
# GNU General Public License for more details.                            #
#                                                                         #
# You should have received a copy of the GNU General Public License       #
# along with this program.  If not, see http://www.gnu.org/licenses/.     #
##########################COPYRIGHT INFORMATION############################

import sys
import os
import subprocess
from be_mr import *
from jumplist_mr import *
from entropy_mr import *
from extract_registry_hives_mr import *
from mr_registry import *
from GUI_Timeline_mr import *
from remove_duplicates_mr import *
from carve_unallocated_mr import *
from volatility_mr import *
import volley24
from exifdata_mr import *
from extract_ntfs_artifacts_mr import *
from create_kml_from_exif_mr import *
from plist_processor import *
from filename_search_mr import *
import ga_cookie_cruncher_mr

### SPLASHSCREEN ###########################################################################

def splashscreen():

    intro_splashscreen = buttonbox(msg='', image='/usr/share/mantaray/images/Mantaray_Logo_Template_Full_Screen.gif',
                                   title='MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com',
                                   choices=('Continue', 'About', 'License', 'Support', 'System Requirements', 'Exit'))

    if intro_splashscreen == "About":

        try:
            subprocess.call(['zenity --text-info --filename=/usr/share/mantaray/Tools/Python/about.txt '
                             '--title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" '
                             '--width 800 --height 625'], shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            sys.exit(0)
        splashscreen()

    if intro_splashscreen == "License":

        try:
            subprocess.call(['zenity --text-info --filename=/usr/share/mantaray/Tools/Python/MR_GNU_License.txt '
                             '--title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" '
                             '--width 800 --height 400'], shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            sys.exit(0)
        splashscreen()

    if intro_splashscreen == "Support":

        try:
            subprocess.call(['zenity --text-info --filename=/usr/share/mantaray/Tools/Python/support.txt '
                             '--title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" '
                             '--width 800 --height 400'], shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            sys.exit(0)
        splashscreen()

    if intro_splashscreen == "System Requirements":

        try:
            subprocess.call(['zenity --text-info --filename=/usr/share/mantaray/Tools/Python/sys_requirements.txt '
                             '--title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" '
                             '--width 800 --height 400'], shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            sys.exit(0)
        splashscreen()



    if intro_splashscreen == "Exit":
        sys.exit(0)
    return intro_splashscreen
############################################################################################


# get date/time
now = datetime.datetime.now()

intro_splashscreen = splashscreen()

# disable auto-mount in nautilis - this stops a nautilis window from popping up everytime the mount command is executed
cmd_false = "sudo gsettings set org.gnome.desktop.media-handling automount false && " \
            "sudo gsettings set org.gnome.desktop.media-handling automount-open false && " \
            "sudo gsettings set org.gnome.desktop.media-handling autorun-never true"
try:
    subprocess.call([cmd_false], shell=True)
except:
    print("Autmount false failed")

# Enter Case Information

if intro_splashscreen:

    try:
        msg = "Case Information"
        title = "MantaRay - ManTech Triage & Analysis System"
        fieldNames = ["Case Number","Evidence Number","Examiner Name","Notes"]
        fieldValues = []  # we start with blanks for the values
        fieldValues = multenterbox(msg, title, fieldNames)

    ## Verify fields are not blank

        while 1:
            if fieldValues == None: break
            errmsg = ""
            for i in range(len(fieldNames)):
                if fieldValues[i].strip() == "":
                    errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
            if errmsg == "":
                break # no problems found
            fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)

            #writeln("Reply was: %s" % str(fieldValues))

    except:
        print ("Cancel/Exit chosen")
        sys.exit(0)

    if fieldValues:
        case_number = fieldValues[0]
        #substitute _ for / and \
        if(re.search(" ", case_number)):
            case_number = case_number.replace(" ", "")
            print(case_number)
        if(re.search("/", case_number)):
            case_number = case_number.replace("/", "_")
            print(case_number)
        if(re.search("\\\\", case_number)):
            case_number = case_number.replace("\\", "_")
            print(case_number)
        evidence_number = fieldValues[1]
        examiner_name = fieldValues[2]
        case_notes = fieldValues[3]
        case_number = case_number + "-" + evidence_number + "-MantaRay_" + now.strftime("%Y-%m-%d_%H_%M_%S_%f")
        print("Case Number: " + case_number)
        print("Evidence Number: " + evidence_number)
        print("Examiner Name: " + examiner_name)
        print("Case notes: " + case_notes)


    else:
        print ("Cancel/Exit chosen.")
        sys.exit(0)

##Choose Evidence Type - Image Type

batch_mode = "Single Disk Image"
evidence_path_list = []


if fieldValues: 

    try:
        evidence_type = subprocess.check_output(['zenity --list --radiolist '
                                                 '--title "MantaRay - ManTech Triage & Analysis System		'
                                                 'MantaRayForensics.com" --column="Selection" --column="Evidence Type" '
                                                 '--column="Description" --separator="," '
                                                 'TRUE "Bit-Stream Image" ".dd, .img, .001, .E01" '
                                                 'FALSE "Directory" "Logical Directory" '
                                                 'FALSE "EnCase Logical Evidence File" ".L01" '
                                                 'FALSE "Memory Image" "Forensic Image of RAM" '
                                                 'FALSE "Single File" "Individual File"'
                                                 ' --text="Evidence Type Selection" --width 800 --height 400'],
                                                shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        sys.exit(0)

    if evidence_type:
        evidence_type = evidence_type.strip()
        print("Evidence Type:" + evidence_type)

    else:
        print ("No evidence type was selected.")
        subprocess.call(['zenity --info --title "MantaRay - ManTech Triage & Analysis System" '
                         '--text="No evidence type was selected.  Evidence type is required."'],
                        shell=True, universal_newlines=True)

        sys.exit(0)

##Choose Output Directory

if evidence_type:

    try:
        root_output_dir = subprocess.check_output(['sudo zenity --file-selection --directory --filename="/mnt/hgfs/" '
                                                   '--title "Select Root Output Directory" '
                                                   '--text="Select Output Directory"'],
                                                  shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        sys.exit(0)

    if root_output_dir:
        print("Output Directory:" + root_output_dir.strip())
        #create output directory
        folder_path = root_output_dir.strip() + "/" + case_number
        folder_path = check_for_folder(folder_path, "NONE")
    else:
        print ("No output directory was selected.")
        sys.exit(0)

batch_mode_enabler = ""
batch_mode_enabled = False

if evidence_type == "Bit-Stream Image":
    batch_mode_enabler = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech Triage & '
                                                   'Analysis System		MantaRayForensics.com" --column="Selection" '
                                                   '--column="Processing Mode" --column="Description" --separator="," '
                                                   'FALSE "Enable Batch Mode" "This mode allows for multiple images to'
                                                   'be processed with the same settings automatically " '
                                                   'TRUE "Single Image Mode" "This mode is the standard MantaRay mode'
                                                   'and should be used if there is only 1 image or custom settings for'
                                                   'each image to be processed" --text="Run Mode Selection"'
                                                   ' --width 800 --height 400'], shell=True)

    print(batch_mode_enabler)
    print(type(batch_mode_enabler))
    if batch_mode_enabler.decode().strip() == "Enable Batch Mode":
        batch_mode_enabled = True
    elif batch_mode_enabler.decode().strip() == "Single Image Mode":
        batch_mode_enabled = False
    else:
        print("Error Processing Batch Mode...Exiting Now!")
        sys.exit(0)

##Create and open log file

gui_log_file = folder_path + "/" + case_number + "_MantaRay_logfile.txt"
gui_outfile = open(gui_log_file, 'a')

##Log previous user created information

now = datetime.datetime.now()

gui_outfile.write(now.strftime("%Y-%m-%d %H:%M:%S")+ "\n\n")
gui_outfile.write("Case Number:"+"\t\t"+case_number+"\n"+"Evidence Number:"+"\t"+fieldValues[1]+"\n"+
                  "Examiner Name:"+"\t\t"+fieldValues[2]+"\n\n")
gui_outfile.write("Notes:" +"\t" + fieldValues[3] + "\n\n")
gui_outfile.write("Evidence Type:" + "\t" + evidence_type + "\n")
gui_outfile.write("Output Folder:" + "\t" + folder_path + "\n")

##Choose Processing Scripts

if evidence_type == "Bit-Stream Image":

    try:
        processing_scripts = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech Triage & '
                                                      'Analysis System	MantaRayForensics.com" --column="Selection" '
                                                      '--column="Processing Tool" --column="Description" '
                                                      '--separator="," '

                                                      'FALSE "BulkExtractor" "Scans for a large number of pre-defined '
                                                        'regular expressions" '

                                                      'FALSE "Calculate Entropy" '
                                                      '"Pseudorandom number sequence test (ENT)" '

                                                      'FALSE "Create KML from JPG EXIF Data" "Create Google Earth .kml '
                                                        'file from EXIF data found in JPG images" '

                                                      'FALSE "EXIF Tool" "Read meta information in files" '

                                                      'FALSE "Foremost" "Recover files from a disk image based on '
                                                        'headers and footers (Unallocated Space)" '

                                                      'FALSE "Jumplist Parser" "Windows Vista/7 Jumplist Exploitation" '

                                                      'FALSE "NTFS Artifact Extractor" "\$MFT/\$LogFile/((\$USNJRNL\$J '
                                                        '(Vista/7 Only)) Overt & Shadow Volume Extraction" '

                                                      'FALSE "File Name Search" "Extract files by file name from '
                                                        'OVERT//DELETED//VSS (Windows Only)" '

                                                      'FALSE "PLIST Processor" "Extracts triage data from selected '
                                                        '.plist files" '

                                                      'FALSE "Google Analytics Cookie Cruncher" "Carves and processes '
                                                        'artifacts from Google Analytic Cookies" '

                                                      'FALSE "Registry Hive Extractor//Regripper" "Extract Registry '
                                                        'from overt, deleted, unallocated, shadow volumes, '
                                                        'restore-points & process with RegRipper" '

                                                      'FALSE "Super Timeline" "Parse various log files and artifacts '
                                                        'for timeline analysis"  '
                                                      '--text="Processing Tool Selection   |  '
                                                      ' Evidence Type: Bit-Stream Image" --width 1100 --height 400'],
                                                     shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Bit-Stream Image: Processing Tool Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

    if processing_scripts:
        print("Processing Scripts: " + processing_scripts.strip())
        gui_outfile.write("Processing Scripts:" + "\t" + processing_scripts.strip() + "\n")
    else:
        print ("No processing scripts were selected.")
        gui_outfile.write("Bit-Stream Image: Script Selection - No processing scripts were selected.")
        sys.exit(0)

    try:
        if batch_mode_enabled:
            evidence_path = subprocess.check_output(['zenity --file-selection --directory="/mnt/hgfs/"  '
                                                     '--title "Select Directory with Bit-Stream Images to Process"'],
                                                    shell=True, universal_newlines=True)

        else:
            evidence_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" '
                                                     '--file-filter=""*.DD" "*.dd" "*.IMG" "*.img" "*.001" "*.E01"" '
                                                     '--title "Select Bit-Stream Image to Process"'],
                                                    shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Bit-Stream Image: Image Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

    if evidence_path:
        print("Bit-Stream Image: " + evidence_path.strip())
        gui_outfile.write("Bit-Stream Image:" + "\t" + evidence_path.strip() + "\n")
    else:
        print ("No Image was selected.")
        gui_outfile.write("Bit-Stream Image: Bit-Stream Image Selection - No Bit-stream Image was selected.")
        sys.exit(0)


if evidence_type == "EnCase Logical Evidence File":

    try:
        processing_scripts = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech Triage & '
                                                      'Analysis System		MantaRayForensics.com" '
                                                      '--column="Selection" --column="Processing Tool" '
                                                      '--column="Description" --separator="," '
                                                      'FALSE "BulkExtractor" '
                                                        '"Scans for a large number of predefined regular expressions." '
                                                      'FALSE "Calculate Entropy" '
                                                        '"Pseudorandom number sequence test (ENT)" '
                                                      'FALSE "Create KML from JPG EXIF Data" '
                                                        '"Create Google Earth .kml file from EXIF data found in JPG '
                                                        'images" '
                                                      'FALSE "PLIST Processor" '
                                                        '"Extracts triage data from selected .plist files" '
                                                      'FALSE "Super Timeline" '
                                                        '"Parse various log files and artifacts for timeline analysis" '
                                                      '--text="Processing Tool Selection   |   '
                                                        'Evidence Type: EnCase Logical Evidence File" '
                                                      '--width 1100 --height 400'], shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("EnCase Logical Evidence File: Processing Tool Selection - Aborted by user - "
                          "Cancel/Exit chosen")
        sys.exit(0)

    if processing_scripts:
        print("Processing Scripts: " + processing_scripts)
        gui_outfile.write("Processing Scripts:" + "\t" + processing_scripts + "\n")
    else:
        print ("No processing scripts were selected.")
        gui_outfile.write("EnCase Logical Evidence File: Processing Tool Selection - "
                          "No processing scripts were selected.")
        sys.exit(0)

    try:

        evidence_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" '
                                                 '--file-filter=""*.L01" "*.l01"" '
                                                 '--title "Select EnCase Logical Evidence File to Process"'],
                                                shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("EnCase Logical Evidence File: File Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

if evidence_type == "Directory":

    try:

        processing_scripts = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" '
                                                      '--column="Selection" --column="Processing Tool" --column="Description" --separator="," '
                                                      'FALSE "BulkExtractor" '
                                                        '"Scans for a large number of pre-defined regular expressions" '

                                                      'FALSE "Calculate Entropy" '
                                                        '"Pseudorandom number sequence test (ENT)" '

                                                      'FALSE "Create KML from JPG EXIF Data" '
                                                        '"Create Google Earth .kml file from EXIF data found in '
                                                        'JPG images" '

                                                      'FALSE "Delete Duplicate Files" '
                                                        '"Delete duplicate files from the selected directory '
                                                        '(Recursive)" '

                                                      'FALSE "EXIF Tool" '
                                                        '"Read meta information in files" '

                                                      'FALSE "GA Cookies" '
                                                        '"Scan and Process Google Analytic Cookies"'

                                                      'FALSE "PLIST Processor" '
                                                        '"Extracts triage data from selected .plist files" '

                                                      'FALSE "Super Timeline" '
                                                        '"Parse various log files and artifacts for timeline analysis" '
                                                      '--text="Processing Tool Selection   |  '
                                                      ' Evidence Type: Directory" --width 1100 --height 400'],
                                                     shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Directory: Processing Tool Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

    if processing_scripts:
        print("Processing Scripts: " + processing_scripts.strip())
        gui_outfile.write("Processing Scripts:" + "\t" + processing_scripts.strip() + "\n")
    else:
        print ("No processing scripts were selected.")
        gui_outfile.write("Directory: Processing Tool Selection - No processing scripts were selected.")
        sys.exit(0)

    try:

        evidence_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" --directory '
                                                 '--title "Select Directory to Process"'],
                                                shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Directory: Directory Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

if evidence_type == "Memory Image":

    try:
        processing_scripts = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech Triage & '
                                                      'Analysis System		MantaRayForensics.com" '
                                                      '--column="Selection" --column="Processing Tool" '
                                                      '--column="Description" --separator="," '
                                                      'FALSE "BulkExtractor" '
                                                        '"Scans for a large number of pre-defined regular expressions" '

                                                      'FALSE "GA Cookies" '
                                                        '"Scan and Process Google Analytic Cookies" '

                                                      'FALSE "Volatility" '
                                                        '"Extraction of digital artifacts from volatile memory" '

                                                      '--text="Processing Tool Selection   |   '
                                                        'Evidence Type: Memory Image" '
                                                      '--width 1100 --height 400'], shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Memory Image: Processing Tool Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

    if processing_scripts:
        print("Processing Scripts: " + processing_scripts.strip())
        gui_outfile.write("Processing Scripts:" + "\t" + processing_scripts.strip() + "\n")
    else:
        print ("No processing scripts were selected.")
        gui_outfile.write("Memory Image: Processing Tool Selection - No processing scripts were selected.")
        sys.exit(0)

    try:

        evidence_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" '
                                                 '--file-filter=""*.DD" "*.dd" "*.IMG" "*.img" "*.001" "*.BIN" "*.bin" '
                                                    '"*.MEM" "*.mem" " '

                                                 '--title "Select Memory Image to Process"'],
                                                shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Memory Image: Directory Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

if evidence_type == "Single File":

    try:

        processing_scripts = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech Triage & '
                                                      'Analysis System		MantaRayForensics.com" --column="Selection" '
                                                      '--column="Processing Tool" --column="Description" '
                                                      '--separator="," '

                                                      'FALSE "BulkExtractor" '
                                                        '"Scans for a large number of predefined regular expressions." '

                                                      'FALSE "Calculate Entropy" '
                                                        '"Pseudorandom number sequence test (ENT)" '

                                                      'FALSE "Create KML from JPG EXIF Data" '
                                                        '"Create Google Earth .kml file from EXIF data found in '
                                                        'JPG images" '

                                                      'FALSE "GA Cookies" '
                                                        '"Scan for and Process Google Analytic Cookies"'

                                                      '--text="Processing Tool Selection   |   Evidence Type: '
                                                        'Single File" --width 1100 --height 400'],
                                                     shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Single File: Processing Tool Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

    if processing_scripts:
        print("Processing Scripts: " + processing_scripts.strip())
        gui_outfile.write("Processing Scripts:" + "\t" + processing_scripts.strip() + "\n")
    else:
        print ("No processing scripts were selected.")
        gui_outfile.write("Single File: Processing Tool Selection - No processing scripts were selected.")
        sys.exit(0)

    try:
        evidence_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" '
                                                 '--title "Select Single File to Process"'],
                                                shell=True, universal_newlines=True)

    except:
        print ("Cancel/Exit chosen")
        gui_outfile.write("Single File: Directory Selection - Aborted by user - Cancel/Exit chosen")
        sys.exit(0)

#split string on comma
processing_scripts = processing_scripts.strip()
processing_scripts_list = processing_scripts.split(",")

#set debug option
evidence_path = evidence_path.strip()
print(evidence_path)
print(type(evidence_path))
evidence = False

if batch_mode_enabled:
    if os.path.isdir(evidence_path):
        for root, dirs, files in os.walk(evidence_path):
            for fname in files:
                quoted_path = os.path.join(root, fname)

                if fname.lower().endswith(".e01"):
                    evidence_path_list.append(quoted_path)
                elif fname.lower().endswith(".dd"):
                    evidence_path_list.append(quoted_path)
                elif fname.lower().endswith(".001"):
                    evidence_path_list.append(quoted_path)
                elif fname.lower().endswith(".img"):
                    evidence_path_list.append(quoted_path)

    else:
        print("Evidence is not a valid directory to scan...Exiting Now!")
        sys.exit(0)

else:
    if os.path.isfile(evidence_path):
        evidence_path = '\"' + evidence_path.strip() + '\"'
        evidence_path_list.append(evidence_path)

# Debugging - Comment Out
import pprint
pprint.pprint(evidence_path_list)

if len(evidence_path_list) == 0 and batch_mode_enabled:
    print("No Suitable Images discovered. Please ensure the supported file extensions are present")
    print("Supported Formats: EnCase v6 E01, DD, dd, IMG, img, 001")
    print("Exiting Now!")
    sys.exit(0)

try:

    debug_mode = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech Triage & '
                                          'Analysis System		MantaRayForensics.com" '
                                          '--column="Selection" --column="Debug Option" --column="Description" '
                                          '--column="Warning" --separator="," '

                                          'TRUE "OFF" "Default mode, no verbose error logging" "" '

                                          'FALSE "ON" "Debugging mode, verbose error logging" '
                                            '"All processes will stop at first error" '

                                          '--text="Debugging Option Selection" --width 800 --height 175'],
                                         shell=True, universal_newlines=True)

except:
    print ("Cancel/Exit chosen")
    gui_outfile.write("Debug Options: Aborted by user - Cancel/Exit chosen")
    sys.exit(0)

if debug_mode:
    debug_mode = debug_mode.strip()
    print("Debug Mode: " + debug_mode)
    gui_outfile.write("Debug Mode:" + "\t" + debug_mode + "\n")

#Gather User Specified Options for Processing Tools

for x in processing_scripts_list:

    if x == 'BulkExtractor':

        try:
            bulkextractor_options = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech '
                                                             'Triage & Analysis System		MantaRayForensics.com" '
                                                             '--column="Selection" --column="Processing Option" '
                                                             '--column="Description" --separator="," '

                                                             'FALSE "Keyword List" '
                                                                '"Search for case specific keyword list" '

                                                             'FALSE "Whitelist" '
                                                                '"Remove known features (artifacts) from '
                                                                'process output" '

                                                             '--text="Processing Options - BulkExtractor" '
                                                             '--width 800 --height 400'],
                                                            shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            gui_outfile.write("BulkExtractor Options: Processing Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)

        if bulkextractor_options:
            print("BulkExtractor Options: " + bulkextractor_options.strip())
            gui_outfile.write("BulkExtractor:" + "\t" + bulkextractor_options.strip() + "\n")
        else:
            print ("BulkExtractor Options: No options were selected.")
            gui_outfile.write("BulkExtractor Options: Processing Options - No processing scripts were selected.")
            #sys.exit(0)

        bulkextractor_options = bulkextractor_options.strip()
        bulkextractor_options_list = bulkextractor_options.split(",")

        #initialize bulk_extractor options
        keyword_list_path = "NONE"
        whitelist_path = "NONE"

        for item in bulkextractor_options_list:
            if item == 'Keyword List':
                keyword_list_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" '
                                                             '--title "Select BulkExtractor Keyword List"'],
                                                            shell=True, universal_newlines=True)
                print("Keyword List: " + keyword_list_path.strip())
                gui_outfile.write("Keyword List:" + "\t" + keyword_list_path.strip() + "\n")

            if item == 'Whitelist':

                whitelist_path = subprocess.check_output(['zenity --file-selection --filename="/mnt/hgfs/" '
                                                          '--title "Select BulkExtractor Whitelist"'],
                                                         shell=True, universal_newlines=True)
                print("Whitelist: " + whitelist_path.strip())
                gui_outfile.write("Whitelist:" + "\t" + whitelist_path.strip() + "\n")

        try:
            bulkextractor_processor = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech '
                                                               'Triage & Analysis System		MantaRayForensics.com" '
                                                               '--column="Selection" --column="Processor Performance" '
                                                               '--column="Description" --separator="," '
                                                               ''
                                                               'FALSE "Speed-Slow" '
                                                                '"Minimum Processing Cores" '

                                                               'TRUE "Speed-Med" '
                                                                '"Medium Processing Cores (Recommended)" '

                                                               'FALSE "Speed-Fast" '
                                                                '"Maximum Processing Cores '
                                                                '(Warning - Processor Intensive)" '

                                                               '--text="Processing Performance - BulkExtractor" '
                                                               '--width 800 --height 400'],
                                                              shell=True, universal_newlines=True)

        except:

            print ("Cancel/Exit chosen")
            gui_outfile.write("BulkExtractor Processor: Processor Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)


        print("BulkExtractor Performance: " + bulkextractor_processor.strip())
        gui_outfile.write("BulkExtractor Performance:" + "\t" + bulkextractor_processor.strip() + "\n")

        #pass variables to bulk_extractor module

    elif x == 'Foremost':

        try:

            foremost_options = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech Triage &'
                                                        ' Analysis System		MantaRayForensics.com" '
                                                        '--column="Selection" --column="Processing Option" '
                                                        '--column="Description" --separator="," '

                                                        'TRUE "Default File Signatures" '
                                                            '"jpg,gif,png,bmp,avi,exe,mpg,wav,riff,wmv,mov,pdf,ole,doc,'
                                                            'zip,rar,htm,cpp" '

                                                        'FALSE "Configuration File" '
                                                            '"Use configuration file - (/etc/foremost.conf)" '

                                                        '--text="Processing Options - Foremost" '
                                                        '--width 800 --height 400'],
                                                       shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            gui_outfile.write("Foremost Options: Processing Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)

        print("Foremost Options: " + foremost_options.strip())
        gui_outfile.write("Foremost Options:" + "\t" + foremost_options.strip() + "\n")

        #Let user select individual file signatures to carve for
        if(re.search('Default', foremost_options)):
            cmd_string = "jpg,gif,bmp,avi,exe,mpg,wav,mov,pdf,ole,doc,zip,rar,htm,wmv,png,mp4"

    elif x == 'Super Timeline':
        # If you would like to enable plaso, uncomment lines 467-477 and comment out line 466.
        #  This should only be modified if you are an advanced user.
        super_timeline_options = "Log2Timeline"
        """
        try:
            super_timeline_options = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" --column="Selection" --column="Processing Option" --column="Tool Version" --column="Description" --separator="," FALSE "Log2Timeline" "v. 0.65" "Original timeline tool, outputs mactime, bodyfile, and csv format" FALSE "Plaso" "v. 1.1" "Updated timeline tool, outputs a .dmp file for further processing into a csv, raw, or dynamic output." --text="Select Timeline Tool" --width 800 --height 400'], shell=True, universal_newlines=True)
            super_timeline_options = super_timeline_options.strip()
            print("Timeline Tool: " + super_timeline_options)
            gui_outfile.write("Timeline Tool: " + "\t" + super_timeline_options + "\n")
        except:
            print ("Cancel/Exit chosen")
            gui_outfile.write("Timeline Processor: Processor Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)
        """
        if(super_timeline_options == "Plaso"):

            try:
                plaso_output_options = subprocess.check_output(['zenity --list --checklist --title "MantaRay - ManTech '
                                                                'Triage & Analysis System		MantaRayForensics.com" '
                                                                '--column="Selection" --column="Psort Output" '
                                                                '--column="Description" --separator="," '

                                                                'FALSE "CSV" '
                                                                    '"CSV Format, similar to the Log2Timeline csv '
                                                                    'output" '

                                                                'FALSE "Rawpy" '
                                                                    '"Prints out raw text file of Event Objects" '

                                                                'FALSE "Dynamic" '
                                                                    '"CSV format, Contains fields " '

                                                                '--text="Select Plaso Options" '
                                                                '--width 800 --height 400'],
                                                               shell=True, universal_newlines=True)

                plaso_output_options = plaso_output_options.strip()
                print("Plaso Output Options: " + plaso_output_options)
                gui_outfile.write("Plaso Output Options: " + "\t" + plaso_output_options + "\n")
            except:
                print ("Cancel/Exit chosen")
                gui_outfile.write("Timeline Processor: Processor Options - Aborted by user - Cancel/Exit chosen")
                sys.exit(0)

            #Add Processing Speed to Plaso
            try:
                plaso_processor = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech '
                                                           'Triage & Analysis System		MantaRayForensics.com" '
                                                           '--column="Selection" --column="Processor Performance" '
                                                           '--column="Description" --separator="," '

                                                           'FALSE "Speed-Slow" '
                                                            '"Minimum Processing Cores" '

                                                           'TRUE "Speed-Med" '
                                                            '"Medium Processing Cores (Recommended)" '

                                                           'FALSE "Speed-Fast" '
                                                            '"Maximum Processing Cores (Warning - Processor Intensive)" '

                                                           '--text="Processing Performance - Plaso" '
                                                           '--width 800 --height 400'],
                                                          shell=True, universal_newlines=True)

            except:

                print ("Cancel/Exit chosen")
                gui_outfile.write("Plaso Processor: Processor Options - Aborted by user - Cancel/Exit chosen")
                sys.exit(0)
        

        elif(super_timeline_options == "Log2Timeline"):
            plaso_output_options = "NONE"
            plaso_processor = "NONE"
        try:
            select_timezone = subprocess.check_output(['zenity --question --title "MantaRay - ManTech Triage & '
                                                       'Analysis System		MantaRayForensics.com" '
                                                       '--text="Non-english unicode timezones must be set manually.  '
                                                       'If there is a chance the case has non-english timezones, verify'
                                                       ' timezone using other methods and set this option manually.  '
                                                       'A future release of MantaRay will provide automatic '
                                                       'verification of all timezones prior to this selction option. '
                                                       ' Do you want to set the SuperTimeline timezone manually?" '
                                                       '--width 800 --height 200'], shell=True, universal_newlines=True)

            user_defined_timezone = subprocess.check_output(['zenity --list --radiolist --title "MantaRay - ManTech '
                                                             'Triage & Analysis System		MantaRayForensics.com" '
                                                             '--column="Selection" --column="Timezone" --separator="," '
                                                             'TRUE "UTC" FALSE "AKST9AKDT" FALSE "Africa/Abidjan" FALSE "Africa/Accra" FALSE "Africa/Addis_Ababa" FALSE "Africa/Algiers" FALSE "Africa/Asmara" FALSE "Africa/Asmera" FALSE "Africa/Bamako" FALSE "Africa/Bangui" FALSE "Africa/Banjul" FALSE "Africa/Bissau" FALSE "Africa/Blantyre" FALSE "Africa/Brazzaville" FALSE "Africa/Bujumbura" FALSE "Africa/Cairo" FALSE "Africa/Casablanca" FALSE "Africa/Ceuta" FALSE "Africa/Conakry" FALSE "Africa/Dakar" FALSE "Africa/Dar_es_Salaam" FALSE "Africa/Djibouti" FALSE "Africa/Douala" FALSE "Africa/El_Aaiun" FALSE "Africa/Freetown" FALSE "Africa/Gaborone" FALSE "Africa/Harare" FALSE "Africa/Johannesburg" FALSE "Africa/Juba" FALSE "Africa/Kampala" FALSE "Africa/Khartoum" FALSE "Africa/Kigali" FALSE "Africa/Kinshasa" FALSE "Africa/Lagos" FALSE "Africa/Libreville" FALSE "Africa/Lome" FALSE "Africa/Luanda" FALSE "Africa/Lubumbashi" FALSE "Africa/Lusaka" FALSE "Africa/Malabo" FALSE "Africa/Maputo" FALSE "Africa/Maseru" FALSE "Africa/Mbabane" FALSE "Africa/Mogadishu" FALSE "Africa/Monrovia" FALSE "Africa/Nairobi" FALSE "Africa/Ndjamena" FALSE "Africa/Niamey" FALSE "Africa/Nouakchott" FALSE "Africa/Ouagadougou" FALSE "Africa/Porto-Novo" FALSE "Africa/Sao_Tome" FALSE "Africa/Timbuktu" FALSE "Africa/Tripoli" FALSE "Africa/Tunis" FALSE "Africa/Windhoek" FALSE "America/Adak" FALSE "America/Anchorage" FALSE "America/Anguilla" FALSE "America/Antigua" FALSE "America/Araguaina" FALSE "America/Argentina/Buenos_Aires" FALSE "America/Argentina/Catamarca" FALSE "America/Argentina/ComodRivadavia" FALSE "America/Argentina/Cordoba" FALSE "America/Argentina/Jujuy" FALSE "America/Argentina/La_Rioja" FALSE "America/Argentina/Mendoza" FALSE "America/Argentina/Rio_Gallegos" FALSE "America/Argentina/Salta" FALSE "America/Argentina/San_Juan" FALSE "America/Argentina/San_Luis" FALSE "America/Argentina/Tucuman" FALSE "America/Argentina/Ushuaia" FALSE "America/Aruba" FALSE "America/Asuncion" FALSE "America/Atikokan" FALSE "America/Atka" FALSE "America/Bahia" FALSE "America/Bahia_Banderas" FALSE "America/Barbados" FALSE "America/Belem" FALSE "America/Belize" FALSE "America/Blanc-Sablon" FALSE "America/Boa_Vista" FALSE "America/Bogota" FALSE "America/Boise" FALSE "America/Buenos_Aires" FALSE "America/Cambridge_Bay" FALSE "America/Campo_Grande" FALSE "America/Cancun" FALSE "America/Caracas" FALSE "America/Catamarca" FALSE "America/Cayenne" FALSE "America/Cayman" FALSE "America/Chicago" FALSE "America/Chihuahua" FALSE "America/Coral_Harbour" FALSE "America/Cordoba" FALSE "America/Costa_Rica" FALSE "America/Cuiaba" FALSE "America/Curacao" FALSE "America/Danmarkshavn" FALSE "America/Dawson" FALSE "America/Dawson_Creek" FALSE "America/Denver" FALSE "America/Detroit" FALSE "America/Dominica" FALSE "America/Edmonton" FALSE "America/Eirunepe" FALSE "America/El_Salvador" FALSE "America/Ensenada" FALSE "America/Fort_Wayne" FALSE "America/Fortaleza" FALSE "America/Glace_Bay" FALSE "America/Godthab" FALSE "America/Goose_Bay" FALSE "America/Grand_Turk" FALSE "America/Grenada" FALSE "America/Guadeloupe" FALSE "America/Guatemala" FALSE "America/Guayaquil" FALSE "America/Guyana" FALSE "America/Halifax" FALSE "America/Havana" FALSE "America/Hermosillo" FALSE "America/Indiana/Indianapolis" FALSE "America/Indiana/Knox" FALSE "America/Indiana/Marengo" FALSE "America/Indiana/Petersburg" FALSE "America/Indiana/Tell_City" FALSE "America/Indiana/Vevay" FALSE "America/Indiana/Vincennes" FALSE "America/Indiana/Winamac" FALSE "America/Indianapolis" FALSE "America/Inuvik" FALSE "America/Iqaluit" FALSE "America/Jamaica" FALSE "America/Jujuy" FALSE "America/Juneau" FALSE "America/Kentucky/Louisville" FALSE "America/Kentucky/Monticello" FALSE "America/Knox_IN" FALSE "America/Kralendijk" FALSE "America/La_Paz" FALSE "America/Lima" FALSE "America/Los_Angeles" FALSE "America/Louisville" FALSE "America/Lower_Princes" FALSE "America/Maceio" FALSE "America/Managua" FALSE "America/Manaus" FALSE "America/Marigot" FALSE "America/Martinique" FALSE "America/Matamoros" FALSE "America/Mazatlan" FALSE "America/Mendoza" FALSE "America/Menominee" FALSE "America/Merida" FALSE "America/Metlakatla" FALSE "America/Mexico_City" FALSE "America/Miquelon" FALSE "America/Moncton" FALSE "America/Monterrey" FALSE "America/Montevideo" FALSE "America/Montreal" FALSE "America/Montserrat" FALSE "America/Nassau" FALSE "America/New_York" FALSE "America/Nipigon" FALSE "America/Nome" FALSE "America/Noronha" FALSE "America/North_Dakota/Beulah" FALSE "America/North_Dakota/Center" FALSE "America/North_Dakota/New_Salem" FALSE "America/Ojinaga" FALSE "America/Panama" FALSE "America/Pangnirtung" FALSE "America/Paramaribo" FALSE "America/Phoenix" FALSE "America/Port-au-Prince" FALSE "America/Port_of_Spain" FALSE "America/Porto_Acre" FALSE "America/Porto_Velho" FALSE "America/Puerto_Rico" FALSE "America/Rainy_River" FALSE "America/Rankin_Inlet" FALSE "America/Recife" FALSE "America/Regina" FALSE "America/Resolute" FALSE "America/Rio_Branco" FALSE "America/Rosario" FALSE "America/Santa_Isabel" FALSE "America/Santarem" FALSE "America/Santiago" FALSE "America/Santo_Domingo" FALSE "America/Sao_Paulo" FALSE "America/Scoresbysund" FALSE "America/Shiprock" FALSE "America/Sitka" FALSE "America/St_Barthelemy" FALSE "America/St_Johns" FALSE "America/St_Kitts" FALSE "America/St_Lucia" FALSE "America/St_Thomas" FALSE "America/St_Vincent" FALSE "America/Swift_Current" FALSE "America/Tegucigalpa" FALSE "America/Thule" FALSE "America/Thunder_Bay" FALSE "America/Tijuana" FALSE "America/Toronto" FALSE "America/Tortola" FALSE "America/Vancouver" FALSE "America/Virgin" FALSE "America/Whitehorse" FALSE "America/Winnipeg" FALSE "America/Yakutat" FALSE "America/Yellowknife" FALSE "Antarctica/Casey" FALSE "Antarctica/Davis" FALSE "Antarctica/DumontDUrville" FALSE "Antarctica/Macquarie" FALSE "Antarctica/Mawson" FALSE "Antarctica/McMurdo" FALSE "Antarctica/Palmer" FALSE "Antarctica/Rothera" FALSE "Antarctica/South_Pole" FALSE "Antarctica/Syowa" FALSE "Antarctica/Vostok" FALSE "Arctic/Longyearbyen" FALSE "Asia/Aden" FALSE "Asia/Almaty" FALSE "Asia/Amman" FALSE "Asia/Anadyr" FALSE "Asia/Aqtau" FALSE "Asia/Aqtobe" FALSE "Asia/Ashgabat" FALSE "Asia/Ashkhabad" FALSE "Asia/Baghdad" FALSE "Asia/Bahrain" FALSE "Asia/Baku" FALSE "Asia/Bangkok" FALSE "Asia/Beirut" FALSE "Asia/Bishkek" FALSE "Asia/Brunei" FALSE "Asia/Calcutta" FALSE "Asia/Choibalsan" FALSE "Asia/Chongqing" FALSE "Asia/Chungking" FALSE "Asia/Colombo" FALSE "Asia/Dacca" FALSE "Asia/Damascus" FALSE "Asia/Dhaka" FALSE "Asia/Dili" FALSE "Asia/Dubai" FALSE "Asia/Dushanbe" FALSE "Asia/Gaza" FALSE "Asia/Harbin" FALSE "Asia/Hebron" FALSE "Asia/Ho_Chi_Minh" FALSE "Asia/Hong_Kong" FALSE "Asia/Hovd" FALSE "Asia/Irkutsk" FALSE "Asia/Istanbul" FALSE "Asia/Jakarta" FALSE "Asia/Jayapura" FALSE "Asia/Jerusalem" FALSE "Asia/Kabul" FALSE "Asia/Kamchatka" FALSE "Asia/Karachi" FALSE "Asia/Kashgar" FALSE "Asia/Kathmandu" FALSE "Asia/Katmandu" FALSE "Asia/Kolkata" FALSE "Asia/Krasnoyarsk" FALSE "Asia/Kuala_Lumpur" FALSE "Asia/Kuching" FALSE "Asia/Kuwait" FALSE "Asia/Macao" FALSE "Asia/Macau" FALSE "Asia/Magadan" FALSE "Asia/Makassar" FALSE "Asia/Manila" FALSE "Asia/Muscat" FALSE "Asia/Nicosia" FALSE "Asia/Novokuznetsk" FALSE "Asia/Novosibirsk" FALSE "Asia/Omsk" FALSE "Asia/Oral" FALSE "Asia/Phnom_Penh" FALSE "Asia/Pontianak" FALSE "Asia/Pyongyang" FALSE "Asia/Qatar" FALSE "Asia/Qyzylorda" FALSE "Asia/Rangoon" FALSE "Asia/Riyadh" FALSE "Asia/Saigon" FALSE "Asia/Sakhalin" FALSE "Asia/Samarkand" FALSE "Asia/Seoul" FALSE "Asia/Shanghai" FALSE "Asia/Singapore" FALSE "Asia/Taipei" FALSE "Asia/Tashkent" FALSE "Asia/Tbilisi" FALSE "Asia/Tehran" FALSE "Asia/Tel_Aviv" FALSE "Asia/Thimbu" FALSE "Asia/Thimphu" FALSE "Asia/Tokyo" FALSE "Asia/Ujung_Pandang" FALSE "Asia/Ulaanbaatar" FALSE "Asia/Ulan_Bator" FALSE "Asia/Urumqi" FALSE "Asia/Vientiane" FALSE "Asia/Vladivostok" FALSE "Asia/Yakutsk" FALSE "Asia/Yekaterinburg" FALSE "Asia/Yerevan" FALSE "Atlantic/Azores" FALSE "Atlantic/Bermuda" FALSE "Atlantic/Canary" FALSE "Atlantic/Cape_Verde" FALSE "Atlantic/Faeroe" FALSE "Atlantic/Faroe" FALSE "Atlantic/Jan_Mayen" FALSE "Atlantic/Madeira" FALSE "Atlantic/Reykjavik" FALSE "Atlantic/South_Georgia" FALSE "Atlantic/St_Helena" FALSE "Atlantic/Stanley" FALSE "Australia/ACT" FALSE "Australia/Adelaide" FALSE "Australia/Brisbane" FALSE "Australia/Broken_Hill" FALSE "Australia/Canberra" FALSE "Australia/Currie" FALSE "Australia/Darwin" FALSE "Australia/Eucla" FALSE "Australia/Hobart" FALSE "Australia/LHI" FALSE "Australia/Lindeman" FALSE "Australia/Lord_Howe" FALSE "Australia/Melbourne" FALSE "Australia/NSW" FALSE "Australia/North" FALSE "Australia/Perth" FALSE "Australia/Queensland" FALSE "Australia/South" FALSE "Australia/Sydney" FALSE "Australia/Tasmania" FALSE "Australia/Victoria" FALSE "Australia/West" FALSE "Australia/Yancowinna" FALSE "Brazil/Acre" FALSE "Brazil/DeNoronha" FALSE "Brazil/East" FALSE "Brazil/West" FALSE "CET" FALSE "CST6CDT" FALSE "Canada/Atlantic" FALSE "Canada/Central" FALSE "Canada/East-Saskatchewan" FALSE "Canada/Eastern" FALSE "Canada/Mountain" FALSE "Canada/Newfoundland" FALSE "Canada/Pacific" FALSE "Canada/Saskatchewan" FALSE "Canada/Yukon" FALSE "Chile/Continental" FALSE "Chile/EasterIsland" FALSE "Cuba" FALSE "EET" FALSE "EST" FALSE "EST5EDT" FALSE "Egypt" FALSE "Eire" FALSE "Etc/GMT" FALSE "Etc/GMT+0" FALSE "Etc/UCT" FALSE "Etc/UTC" FALSE "Etc/Universal" FALSE "Etc/Zulu" FALSE "Europe/Amsterdam" FALSE "Europe/Andorra" FALSE "Europe/Athens" FALSE "Europe/Belfast" FALSE "Europe/Belgrade" FALSE "Europe/Berlin" FALSE "Europe/Bratislava" FALSE "Europe/Brussels" FALSE "Europe/Bucharest" FALSE "Europe/Budapest" FALSE "Europe/Chisinau" FALSE "Europe/Copenhagen" FALSE "Europe/Dublin" FALSE "Europe/Gibraltar" FALSE "Europe/Guernsey" FALSE "Europe/Helsinki" FALSE "Europe/Isle_of_Man" FALSE "Europe/Istanbul" FALSE "Europe/Jersey" FALSE "Europe/Kaliningrad" FALSE "Europe/Kiev" FALSE "Europe/Lisbon" FALSE "Europe/Ljubljana" FALSE "Europe/London" FALSE "Europe/Luxembourg" FALSE "Europe/Madrid" FALSE "Europe/Malta" FALSE "Europe/Mariehamn" FALSE "Europe/Minsk" FALSE "Europe/Monaco" FALSE "Europe/Moscow" FALSE "Europe/Nicosia" FALSE "Europe/Oslo" FALSE "Europe/Paris" FALSE "Europe/Podgorica" FALSE "Europe/Prague" FALSE "Europe/Riga" FALSE "Europe/Rome" FALSE "Europe/Samara" FALSE "Europe/San_Marino" FALSE "Europe/Sarajevo" FALSE "Europe/Simferopol" FALSE "Europe/Skopje" FALSE "Europe/Sofia" FALSE "Europe/Stockholm" FALSE "Europe/Tallinn" FALSE "Europe/Tirane" FALSE "Europe/Tiraspol" FALSE "Europe/Uzhgorod" FALSE "Europe/Vaduz" FALSE "Europe/Vatican" FALSE "Europe/Vienna" FALSE "Europe/Vilnius" FALSE "Europe/Volgograd" FALSE "Europe/Warsaw" FALSE "Europe/Zagreb" FALSE "Europe/Zaporozhye" FALSE "Europe/Zurich" FALSE "GB" FALSE "GB-Eire" FALSE "GMT" FALSE "GMT+0" FALSE "GMT-0" FALSE "GMT0" FALSE "Greenwich" FALSE "HST" FALSE "Hongkong" FALSE "Iceland" FALSE "Indian/Antananarivo" FALSE "Indian/Chagos" FALSE "Indian/Christmas" FALSE "Indian/Cocos" FALSE "Indian/Comoro" FALSE "Indian/Kerguelen" FALSE "Indian/Mahe" FALSE "Indian/Maldives" FALSE "Indian/Mauritius" FALSE "Indian/Mayotte" FALSE "Indian/Reunion" FALSE "Iran" FALSE "Israel" FALSE "JST-9" FALSE "Jamaica" FALSE "Japan" FALSE "Kwajalein" FALSE "Libya" FALSE "MET" FALSE "MST" FALSE "MST7MDT" FALSE "Mexico/BajaNorte" FALSE "Mexico/BajaSur" FALSE "Mexico/General" FALSE "NZ" FALSE "NZ-CHAT" FALSE "Navajo" FALSE "PRC" FALSE "PST8PDT" FALSE "Pacific/Apia" FALSE "Pacific/Auckland" FALSE "Pacific/Chatham" FALSE "Pacific/Chuuk" FALSE "Pacific/Easter" FALSE "Pacific/Efate" FALSE "Pacific/Enderbury" FALSE "Pacific/Fakaofo" FALSE "Pacific/Fiji" FALSE "Pacific/Funafuti" FALSE "Pacific/Galapagos" FALSE "Pacific/Gambier" FALSE "Pacific/Guadalcanal" FALSE "Pacific/Guam" FALSE "Pacific/Honolulu" FALSE "Pacific/Johnston" FALSE "Pacific/Kiritimati" FALSE "Pacific/Kosrae" FALSE "Pacific/Kwajalein" FALSE "Pacific/Majuro" FALSE "Pacific/Marquesas" FALSE "Pacific/Midway" FALSE "Pacific/Nauru" FALSE "Pacific/Niue" FALSE "Pacific/Norfolk" FALSE "Pacific/Noumea" FALSE "Pacific/Pago_Pago" FALSE "Pacific/Palau" FALSE "Pacific/Pitcairn" FALSE "Pacific/Pohnpei" FALSE "Pacific/Ponape" FALSE "Pacific/Port_Moresby" FALSE "Pacific/Rarotonga" FALSE "Pacific/Saipan" FALSE "Pacific/Samoa" FALSE "Pacific/Tahiti" FALSE "Pacific/Tarawa" FALSE "Pacific/Tongatapu" FALSE "Pacific/Truk" FALSE "Pacific/Wake" FALSE "Pacific/Wallis" FALSE "Pacific/Yap" FALSE "Poland" FALSE "Portugal" FALSE "ROC" FALSE "ROK" FALSE "Singapore" FALSE "Turkey" FALSE "UCT" FALSE "US/Alaska" FALSE "US/Aleutian" FALSE "US/Arizona" FALSE "US/Central" FALSE "US/East-Indiana" FALSE "US/Eastern" FALSE "US/Hawaii" FALSE "US/Indiana-Starke" FALSE "US/Michigan" FALSE "US/Mountain" FALSE "US/Pacific" FALSE "US/Pacific-New" FALSE "US/Samoa" FALSE "Universal" FALSE "W-SU" FALSE "WET" FALSE "Zulu" '
                                                             '--text="Timezone Selection" --width 800 --height 800'],
                                                            shell=True, universal_newlines=True)

            user_defined_timezone = user_defined_timezone.strip()
            print("Timezone Option: " + user_defined_timezone)
            gui_outfile.write("Timezone option: " + "\t" + user_defined_timezone + "\n")

        except:
            user_defined_timezone = "NONE"
            print("Timezone Option: User selected no/cancel rather than set timezone manually")
            gui_outfile.write("Timezone Option: User selected no/cancel rather than set timezone manually" + "\n")


    elif x == 'Registry Hive Extractor//Regripper':

        try:

            registry_extractor_options = subprocess.check_output(['zenity --list --checklist --title "MantaRay - '
                                                                  'ManTech Triage & Analysis System		'
                                                                  'MantaRayForensics.com" '
                                                                  '--column="Selection" '
                                                                  '--column="Processing Option" '
                                                                  '--column="Description" '
                                                                  '--separator="," '

                                                                  'FALSE "Overt,Deleted,Restore-Points" '

                                                                    '"Overt/Deleted/Restore-Points(WinXP) '
                                                                    'Registry Hives" FALSE "Unallocated" '
                                                                    '"Unallocated Registry Hives (regf Header - 50MB Length)" FALSE "Shadow Volumes" "Shadow Volume Registry Hives (Windows Vista/7)" --text="Processing Options - Registry Extractor" --width 800 --height 400'], shell=True, universal_newlines=True)

        except:
            print ("Cancel/Exit chosen")
            gui_outfile.write("Registry Extractor Options: Processing Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)

        if registry_extractor_options:
            print("Registry Extractor Options: " + registry_extractor_options.strip())
            gui_outfile.write("Registry Extractor Options:" + "\t" + registry_extractor_options.strip() + "\n")
        else:
            print ("Registry Extractor Options: No options were selected.")
            gui_outfile.write("Registry Extractor Options: Processing Options - No processing scripts were selected.")
            sys.exit(0)

    elif x == 'File Name Search':
        try:

            searchfile = enterbox(msg="Please Enter the File Name to search. ie. index.dat", title='Enter File Name',default='',strip=True,image=None,root=None)

        except:
            print ("Cancel/Exit chosen")
            gui_outfile.write("File Name Search Options: Processing Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)

    elif x == 'Volatility':

        ###############################################
        ####### Volatility Profile Selection ##########

        # Get available profiles 1

        vol_chk_cmd = "vol.py --info"
        raw_output = subprocess.check_output([vol_chk_cmd], shell=True)
        #print(raw_output)
        raw_output = raw_output.decode()
        #print (type(raw_output))

        # Parse output 
        #print(raw_output)
        raw_output2 = raw_output.split("Profiles\n--------\n")
        #print(raw_output2)
        raw_output2a = raw_output2[1].split("\n\n")
        raw_output3 = raw_output2a[0].split("\n")
        #print(raw_output3)
        profile_array = []
        for item in raw_output3:
            if item:
                if item.__contains__("Profiles") or item.__contains__("-------"):
                    pass
                else:
                    item2 = item.split("-")
                    profile_array.append(item2[0].strip(" "))

        # Build zentiy command

        zen_cmd = """zenity --list --radiolist --title "MantaRay - ManTech Triage & Analysis System        MantaRayForensics.com" --column="Selection" --column="Profile Name" --separator="," """ # removed  True "Select Custom Profile"

        for profile in profile_array:
            zen_cmd += 'False "' + profile + '" '

        zen_cmd += """--text="Volatility Profile Selection\n\nIf you do not see the profile desired, please place the profile .zip file in your volatility install directory's /plugins/overlays/[OS_Type]/." --width 800 --height 400"""

        selected_profile = subprocess.check_output([zen_cmd], shell=True, universal_newlines=True)

        if selected_profile.strip() == "Select Custom Profile":
            ### Allow user to add new profile ###

            # Prompt to select .zip file if mac/linux

            extra_profile = subprocess.check_output(['zenity --file-selection --filename="/home" --file-filter=""*.zip" "*.ZIP"" --title "Select Volatility Profile .zip file to load"'], shell=True, universal_newlines=True)#.decode()

            extra_profile = extra_profile.strip()

            if not os.path.isfile(extra_profile):
                print (extra_profile)
                sys.exit(1)

            zen_cmd = """zenity --list --radiolist --title "MantaRay - ManTech Triage & Analysis System        MantaRayForensics.com" --column="Selection" --column="Profile Name" --separator="," False "Windows" False "Macintosh" False "Linux" --text="Volatility Profile Selection\n\n Please select OS Type of the Memory image" --width 800 --height 400"""
            os_selection = subprocess.check_output([zen_cmd], shell=True).strip()
            os_selection = os_selection.decode()
            if os_selection == "Windows":
                os_selection = "windows"
            elif os_selection == "Macintosh":
                os_selection = "mac"
            elif os_selection == "Linux":
                os_selection = "linux"
            try:
                subprocess.call("sudo cp " + extra_profile + " '/usr/lib/python2.7/dist-packages/volatility/plugins/overlays/" + os_selection + "/'", shell=True)
            except :
                print ("Unable to copy custom profile\nPlease manually place file in volatility installation directory or /usr/lib/python2.7/dist-packages/volatility/plugins/overlays/" + os_selection)

            # Get available profiles 2

            vol_chk_cmd = "vol.py --info"
            raw_output = subprocess.check_output([vol_chk_cmd], shell=True).decode()

            # Parse output 
            raw_output = raw_output.split("Plugins")

            raw_output = raw_output[0].split("\n")

            profile_array = []
            for item in raw_output:
                if item:
                    if item.__contains__("Profiles") or item.__contains__("-------"):
                        pass
                    else:
                        item2 = item.split("-")
                        profile_array.append(item2[0].strip(" "))

            # Build zentiy command

            zen_cmd = """zenity --list --radiolist --title "MantaRay - ManTech Triage & Analysis System        MantaRayForensics.com" --column="Selection" --column="Profile Name" --separator="," """

            for profile in profile_array:
                zen_cmd += 'False "' + profile + '" '

            zen_cmd += """--text="Volatility Profile Selection\n\nIf you do not see the profile desirred, please place the .zip file in\nvolatility/overlay/linux for linux profiles, \nvolatility/overlay/mac for mac profiles, or\nvolatility/overlay/windows for windows profiles.\n\nVolatility will likely be installed in\n/usr/lib.python2.7/dist-packages/volatility/ though this path may vary depending on your build " --width 800 --height 400"""

            selected_profile = subprocess.check_output([zen_cmd], shell=True, universal_newlines=True)#.decode()

            print ("Selected Volatility Profile: " + selected_profile)

            ####### Volatility Profile Selection ##########
            ###############################################

        ## Allow user to select PID/DUMP options
        processing_options_cmd = """zenity --list --checklist --title "Mantaray - ManTech Triage & Analysis System        MantaRayForensics.com  |  v1.4" --text="The below options provide additional processing options for memory images with Volatility 2.4. \n Though they will provide more information, it will also take more time depending on the resources allocated." --column="Selection" --column="Name" --column="Description" --separator="," FALSE "PID Processing" "Run available plugins across the discovered PIDs" FALSE "Dump Data" "Use the dump directory function to export data from the memory image." """
        proc_options = subprocess.check_output(processing_options_cmd, shell=True)
        proc_options = proc_options.strip()
        proc_options_array = proc_options.decode().split(",")
        pid_enabled = False
        dump_enabled = False
        if "PID Processing" in proc_options_array:
            pid_enabled = True
        if "Dump Data" in proc_options_array:
            dump_enabled = True

        if pid_enabled:
            print("PID Processing: Enabled")

        if dump_enabled:
            print("Dump Plugins: Enabled")

        ## Allow user to select resources to run
        try:
            vol_processor = subprocess.check_output(['zenity --list --radiolist '
                                                     '--title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" --column="Selection" --column="Processor Performance" --column="Description" --separator="," FALSE "Speed-Slow" "Minimum Processing Cores" TRUE "Speed-Med" "Medium Processing Cores (Recommended)" FALSE "Speed-Fast" "Maximum Processing Cores (Warning - Processor Intensive)" --text="Processing Performance - Volatility" --width 800 --height 400'], shell=True, universal_newlines=True)
        except:
            print ("Cancel/Exit chosen")
            gui_outfile.write("Volatility Processor: Processor Options - Aborted by user - Cancel/Exit chosen")
            sys.exit(0)

        ## convert user answer to number of cores to use
        speed = vol_processor.strip()
        #calculate number of processors to use (Speed-Slow, Speed-Fast, Speed-Med
        calc_cores_command = "cat /proc/cpuinfo | grep processor | wc -l"
        num_of_cores = subprocess.check_output([calc_cores_command], shell=True)
        num_of_cores = num_of_cores.decode(encoding='UTF-8')
        num_of_cores = num_of_cores.strip()
        print("This VM has " + str(num_of_cores) +" cores")

        if(num_of_cores == "1"):
            num_threads = 1
        elif(speed == "Speed-Slow"):
            num_threads = 1
        elif(speed == "Speed-Med"):
            num_threads = int(num_of_cores)//2
        elif(speed == "Speed-Fast"):
            num_threads = int(num_of_cores)

        print("Volatility Performance: " + vol_processor.strip())
        gui_outfile.write("Volatility Performance:" + "\t" + vol_processor.strip() + "\n")

    if x == "Google Analytics Cookie Cruncher":

        # Select Parsers to Use
        cmd = 'zenity --list --checklist ' \
              '--title "MantaRay - ManTech Triage & Analysis System		MantaRayForensics.com" ' \
              '--column="Selection" --column="Parser" --column="Description" ' \
              'TRUE "GIF" "This is reccomended by the developer" ' \
              'FALSE "Chrome" "Parse cookies from the Chrome Browser" ' \
              'FALSE "Internet Explorer" "Parse cookies from the Internet Explorer Browser" ' \
              'FALSE "Firefox" "Parse cookies from the Firefox browser" ' \
              'FALSE "Safari" "Parse cookies from the Safari Browser" ' \
              '--text="Select processors for Google Analytic Cookies" ' \
              '--width 800 --height 400'
        ga_parsers = subprocess.check_output([cmd], shell=True).decode().strip()
        gui_outfile.write("Google Analytic Cookie Parsers selected: " + ga_parsers)
        ga_parsers = ga_parsers.lower().split("|")


#add code to Master outfile to break section between input and tool success
gui_outfile.write("\n\n*************************** PROCESSING STATUS ***************************\n")

folder_path_base = folder_path
batch_counter = 0

#loop through processing_scripts and execute each one passing variables to each script


for evidence_path in evidence_path_list:
    batch_counter = batch_counter + 1

    if batch_mode_enabled:
        folder_path = folder_path_base + "/Batch_Item_0" + str(batch_counter) + "_" + str(os.path.basename(evidence_path).strip('\"'))
        # folder_path = '\"' + folder_path + '\"'
        check_for_folder(folder_path, gui_outfile)

    gui_outfile.flush()
    gui_outfile.write("Processing: " + str(evidence_path) + "\n")


    for x in processing_scripts_list:
        print("Processing " + x + " for " + str(os.path.basename(evidence_path)))

        if x == 'BulkExtractor':
            if(whitelist_path != "") and (keyword_list_path != ""):
                if(debug_mode == "ON"):
                    be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), whitelist_path.strip(), bulkextractor_processor, keyword_list_path.strip())
                    gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                else:
                    try:
                        be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), whitelist_path.strip(), bulkextractor_processor, keyword_list_path.strip())
                        gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                    except:
                        print("Call to bulk_extractor failed")
                        gui_outfile.write("Bulk_Extractor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
            elif(whitelist_path != "") and (keyword_list_path == ""):
                if(debug_mode == "ON"):
                    be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), whitelist_path.strip(), bulkextractor_processor, "NONE")
                    gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                else:
                    try:
                        be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), whitelist_path.strip(), bulkextractor_processor, "NONE")
                        gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                    except:
                        print("Call to bulk_extractor failed")
                        gui_outfile.write("Bulk_Extractor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
            elif(whitelist_path == "") and (keyword_list_path != ""):
                if(debug_mode == "ON"):
                    be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), "NONE", bulkextractor_processor, keyword_list_path.strip())
                    gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                else:
                    try:
                        be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), "NONE", bulkextractor_processor, keyword_list_path.strip())
                        gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                    except:
                        print("Call to bulk_extractor failed")
                        gui_outfile.write("Bulk_Extractor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
            elif(whitelist_path == "") and (keyword_list_path == ""):
                if(debug_mode == "ON"):
                    be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), "NONE", bulkextractor_processor, "NONE")
                    gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                else:
                    try:
                        be_mr(evidence_type, case_number, folder_path, evidence_path.strip(), "NONE", bulkextractor_processor, "NONE")
                        gui_outfile.write("Bulk_Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                    except:
                        print("Call to bulk_extractor failed")
                        gui_outfile.write("Bulk_Extractor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x =='Jumplist Parser':
            if(debug_mode == "ON"):
                jumplist_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                gui_outfile.write("Jumplist Parser...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    jumplist_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("Jumplist Parser...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Jumplist parser failed")
                    gui_outfile.write("Jumplist Parser failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'Calculate Entropy':
            if(debug_mode == "ON"):
                    entropy_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("Calculate Entropy...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    entropy_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("Calculate Entropy...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Entropy calculator failed")
                    gui_outfile.write("Calculate Entropy failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'Registry Hive Extractor//Regripper':
            if(debug_mode == "ON"):
                folder_to_process = extract_registry_hives_mr(evidence_type, case_number, folder_path, evidence_path.strip(),registry_extractor_options.strip())
                gui_outfile.write("Registry Hive Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                mr_registry(case_number, folder_to_process, folder_path) #process extracted reg hives w/ rr
                gui_outfile.write("Regripper...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    folder_to_process = extract_registry_hives_mr(evidence_type, case_number, folder_path, evidence_path.strip(),registry_extractor_options.strip())
                    gui_outfile.write("Registry Hive Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Extract Registry hives failed")
                    gui_outfile.write("Registry Hive Extractor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
                try:
                    mr_registry(case_number, folder_to_process, folder_path)
                    gui_outfile.write("Regripper...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to RegRipper failed")
                    gui_outfile.write("RegRipper failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'Super Timeline':
            if(debug_mode == "ON"):
                GUI_Timeline_mr(evidence_type, case_number, folder_path,  evidence_path.strip(), user_defined_timezone, super_timeline_options, plaso_output_options, plaso_processor)
                gui_outfile.write("Super Timeline...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    GUI_Timeline_mr(evidence_type, case_number, folder_path,  evidence_path.strip(), user_defined_timezone, super_timeline_options, plaso_output_options, plaso_processor)
                    gui_outfile.write("Super Timeline...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Super Timeline failed")
                    gui_outfile.write("Super Timeline failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'Delete Duplicate Files':
            if(debug_mode == "ON"):
                remove_duplicates_mr(folder_path, evidence_path.strip())
                gui_outfile.write("Delete Duplicate Files...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    remove_duplicates_mr(folder_path, evidence_path.strip())
                    gui_outfile.write("Delete Duplicate Files...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Remove_Duplicates failed")
                    gui_outfile.write("Remove Duplicates failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x =='Foremost':
            if(re.search('Default', foremost_options)):
                if(debug_mode == "ON"):
                    carve_unallocated_mr(evidence_type, case_number, folder_path, evidence_path.strip(), cmd_string)
                    gui_outfile.write("Foremost...".ljust(35) + "completed successfully".ljust(55) + "\n")
                else:
                    try:
                        carve_unallocated_mr(evidence_type, case_number, folder_path, evidence_path.strip(), cmd_string)
                        gui_outfile.write("Foremost...".ljust(35) + "completed successfully".ljust(55) + "\n")
                    except:
                        print("Call to Foremost failed")
                        gui_outfile.write("Foremost failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
            else:
                if(debug_mode == "ON"):
                    carve_unallocated_mr(evidence_type, case_number, folder_path, evidence_path.strip(), 'Configuration File')
                    gui_outfile.write("Foremost...".ljust(35) + "completed successfully".ljust(55) + "\n")
                else:
                    try:
                        carve_unallocated_mr(evidence_type, case_number, folder_path, evidence_path.strip(), 'Configuration File')
                        gui_outfile.write("Foremost...".ljust(35) + "completed successfully".ljust(55) + "\n")
                    except:
                        print("Call to Foremost failed")
                        gui_outfile.write("Foremost failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'Volatility':
            if(debug_mode == "ON"):
                volley24.main(evidence_path.strip(), selected_profile.strip(), num_threads, folder_path + "/",  pid_enabled, dump_enabled)
                gui_outfile.write("Volatility...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    volley24.main(evidence_path.strip(), selected_profile.strip(), num_threads, folder_path + "/",  pid_enabled, dump_enabled)
                    gui_outfile.write("Volatility...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Volatility failed")
                    gui_outfile.write("Volatility failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x =='EXIF Tool':
            if(debug_mode == "ON"):
                exifdata_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                gui_outfile.write("EXIF Tool...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    exifdata_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("EXIF Tool...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to EXIF Tool failed")
                    gui_outfile.write("EXIF Tool failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'NTFS Artifact Extractor':
            if(debug_mode == "ON"):
                extract_ntfs_artifacts_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                gui_outfile.write("NTFS Artifact Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    extract_ntfs_artifacts_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("NTFS Artifact Extractor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to NTFS Artifact Extractor failed")
                    gui_outfile.write("NTFS Artifact Extractor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'File Name Search':
            if(debug_mode == "ON"):
                filename_search_mr(evidence_type, case_number, folder_path, evidence_path.strip(), searchfile)
                gui_outfile.write("File Name Search...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    filename_search_mr(evidence_type, case_number, folder_path, evidence_path.strip(), searchfile)
                    gui_outfile.write("File Name Search...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to File Name Search failed")
                    gui_outfile.write("File Name Search failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'Create KML from JPG EXIF Data':
            if(debug_mode == "ON"):
                create_kml_from_exif_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                gui_outfile.write("Create KML from JPG EXIF Data...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    create_kml_from_exif_mr(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("Create KML from JPG EXIF Data...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Create KML from JPG EXIF Data failed")
                    gui_outfile.write("Create KML from JPEG EXIF failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")
        elif x == 'PLIST Processor':
            if(debug_mode == "ON"):
                plist_processor(evidence_type, case_number, folder_path, evidence_path.strip())
                gui_outfile.write("PLIST Processor...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    plist_processor(evidence_type, case_number, folder_path, evidence_path.strip())
                    gui_outfile.write("PLIST Processor...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to PLIST Processor failed")
                    gui_outfile.write("PLIST Processor failed...Please reprocess with Debug Mode ON - running MantaRay from command line as root\n")

        elif x == 'Google Analytics Cookie Cruncher':
            if debug_mode == "ON":
                ga_cookie_cruncher_mr.main(evidence_path.strip(), folder_path+"/GA-Cookies", ga_parsers, evidence_type)
                gui_outfile.write("Google Analytic Cookie Cruncher...".ljust(35) + "completed successfully".ljust(55) + "\n")
            else:
                try:
                    ga_cookie_cruncher_mr.main(evidence_path.strip(), folder_path+"/GA-Cookies", ga_parsers, evidence_type)
                    gui_outfile.write("Google Analytic Cookie Cruncher...".ljust(35) + "completed successfully".ljust(55) + "\n")
                except:
                    print("Call to Google Analytics Cookie Parser failed")
                    gui_outfile.write("Google Analytics Cookie Parser failed...Please reprocess with Debug Mode ON and re-run MantaRay\n")

    gui_outfile.write("\n\n###################################################################################\n\n")

gui_outfile.close()

#tell the user the process is done:
done(folder_path_base)


