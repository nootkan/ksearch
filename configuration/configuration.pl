# KSearch v1.7 - Modernized & Secured (2025)
# Original project: KSearch v1.6 (2012) — https://web.archive.org/web/20130805115023/http://www.ksearch.info/
# Modernization & Security Updates © 2025 Van Isle Web Solutions
#
# Parts of this script © 2000 N. Moraitakis & G. Zervas (www.perlfect.com). All rights reserved.
# Originally licensed under GNU GPL v2-or-later; relicensed under GNU GPL v3-or-later.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#  NOTE: If you change one of the options that's marked 're-index'
#  you need to run 'indexer.pl' again. If you change one of the
#  options that's marked 'edit-help-template' you may need to edit
#  the 'help.html' file and your Template file to exclude/include
#  options for accuracy.
#
#########################################
###REQUIRED CONFIGURATION####################

# Where you want the indexer to start (full path; end with /)
# SECURITY: Update these paths to match your actual installation
our $INDEXER_START = '/home/www/YourDomain.com/'; # re-index

# The base url of your site being indexed
# Be sure it corresponds to the $INDEXER_START directory (end with /)
our $BASE_URL = 'https://www.yourdomain.com/';

# The url where ksearch.cgi is located
our $SEARCH_URL = "https://www.yourdomain.com/search/ksearch.cgi";

# The full-path of the ksearch directory (end with /)
our $KSEARCH_DIR = '/home/yourusername/public_html/search/'; # re-index

# If you are going to run the indexer (indexer.cgi) from the web,
# you must set @VALID_REFERERS, $INDEXER_URL and $PASSWORD.
# Pages from the refering domains below can only run the indexer
# SECURITY: Make sure these match your actual domain
our @VALID_REFERERS = ("https://www.yourdomain.com", "https://www.yourdomain.com");
our $INDEXER_URL = "https://www.yourdomain.com/search/indexer.cgi";

# SECURITY: Use a strong password (at least 12 characters with mixed case, numbers, symbols)
# Generate a random password and change this immediately after installation
our $PASSWORD = "CHANGE_THIS_TO_A_STRONG_PASSWORD_NOW"; # required to access INDEXER.CGI

#########################################
###OPTIONAL INDEXER CONFIGURATION##############

# How many words should be used for the description (may be shorter for meta descriptions)
our $DESCRIPTION_LENGTH = 10; # re-index

# Set this to the term number (first term is 0) you want to start your description at.
# This allows you to skip common headers in the body and show meaningful content
# This does not change meta descriptions.
our $DESCRIPTION_START = 0;	# re-index

# Which extensions should be indexed
# options "html, "htm", "shtml", "txt" ...any extensions representing text files
# SECURITY: Only include extensions you want to be searchable
our @FILE_EXTENSIONS = ("html", "htm", "php", "txt"); # re-index

# Set this to 0 if you do not have or do not want to use any DBM module. 
# RECOMMENDED to set to 0 if you do not have the DB_File module.
# SECURITY: Flat file database is more reliable and secure
our $USE_DBM = 0; # re-index

# Set this to 0 if you DO NOT want to save the content of each file in a FLAT FILE database.
# If set to 1, this option INCREASES THE SEARCH SPEED 5-20x or more at the cost of disk space.
# The disk space needed is usually about half the size of the actual file (depends on HTML and script content)
# HIGHLY RECOMMENDED to set to 1.
our $SAVE_CONTENT = 1; # re-index

# If you want to find common terms and add them to the STOP TERMS file
# set this value to the maximum percentage of files that searchable terms can exist in or set it to 0.
# For example: if set to 90, terms that exist in more than 90 percent of all files will be added to the STOP TERMS file
our $IGNORE_COMMON_TERMS = 80; # re-index

# Set this to 1 if you want to create a log file of the indexing routine (saved as log.txt).
# This logs information about each file indexed and the indexer configuration.
# SECURITY: Useful for troubleshooting but may contain sensitive file paths
our $MAKE_LOG = 1;

# To log search information from users, set this to the full path of your log file.
# This option logs the IP, HOST, search query, and results.
# SECURITY: Be careful with privacy implications of logging user searches
# example: $LOG_SEARCH = '/www/kscripts/ksearch/search_log.txt';
our $LOG_SEARCH = '/home/yourusername/public_html/search/database/search_log.txt';

##############################################################
###OPTIONAL PDF INDEXING CONFIGURATION###############################
##############################################################
##  SECURITY WARNING: PDF indexing requires executing shell commands
##  which poses a security risk. Only enable if you absolutely need it
##  and ensure the pdftotext executable is properly secured.
##  You must have Xpdf installed from https://www.foolabs.com/xpdf/
##############################################################

# Set this to the full path of the pdftotext executable from Xpdf
# if you want to index PDF files. You do not need to add .pdf to @FILE_EXTENSIONS above
# SECURITY: Leave empty to disable PDF processing (recommended)
our $PDF_TO_TEXT = '';  # re-index

# Set this to 0 if you do not want to add 'PDF file size' info to the results titles
# if the file is a PDF file (file size info is redundent but is easily readable)
our $PDF_INFO = 0;

#####################################################################
### SEARCH RESULTS CONFIGURATION#####################################

# How many results should be shown per page as default
# Preferably 5, 10, 25, 50, or 100 since these options are given in the search form
our $RESULTS_PER_PAGE = 10;

# The minimum length of terms to search.
# SECURITY: Setting this to at least 1 helps prevent some forms of abuse
our $MIN_TERM_LENGTH = 1;

# If you want the option to display matches in context in the descriptions
# set this to the number of matches per term/phrase you want to display
# (If you want it as a default setting just add the hidden form value
# in your initial search form):
#
# <INPUT type=hidden name="showm" value="your SHOW_MATCHES value">
#
our $SHOW_MATCHES = 10;

# Set this to the number of characters per line you want to
# display in the description (a line per match; for formating purposes)
our $SHOW_MATCHES_LENGTH = 75;

# Set this to 0 if you DO NOT want to allow phrase searches.
our $DO_PHRASES = 1; # edit-help-template

# Set this to 0 if you DO NOT want to allow case sensitive searches.
our $CASE_SENSITIVE = 1; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching within results
our $SEARCH_RESULTS = 1; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching with no restrictions
# (i.e. allow stop-terms and ignore minimum term length limit)
our $ALL = 1; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching META descriptions
our $META_DESCRIPTION = 1;	# re-index if changing from 0; edit-help-template

# Set this to 0 if you DO NOT want to allow searching META keywords
our $META_KEYWORD = 0;	# re-index if changing from 0; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching META authors
our $META_AUTHOR = 0;	# re-index if changing from 0; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching ALTERNATE TEXT such as those used for images
our $ALT_TEXT = 0;	# re-index if changing from 0; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching all LINKS in documents
our $LINKS = 0;	# re-index if changing from 0; # edit-help-template

# Set this to 0 if you DO NOT want to allow searching the URL of all documents
our $URL = 0; # edit-help-template

# Set this to either "Matches" "Scores" "Dates" or "Sizes" (match case)
# to sort results, respectively (default). These options are given in the search form
our $SORT_BY = "Scores";

# Set this to 0 if you DO NOT want to allow users to weight each individual term/phrase.
# Allowable weights are <2-10000>. This setting could effect the score.
# Example query: '<1000>test perl' gives 'test' 1000 times more weight on the score compared to 'perl'.
# SECURITY: User weights are validated to prevent abuse
our $USER_WEIGHTS = 100; # edit-help-template

# Set this to how many times more important it is to find terms/phrases in titles.
# This setting effects the score.
our $TITLE_WEIGHT = 1000; # a value 1 or above

# Set this to how many times more important it is to find terms/phrases in meta descriptions
# This setting effects the score
our $META_DESCRIPTION_WEIGHT = 5; # a value 1 or above

# Set this to how many times more important it is to find terms/phrases in meta keywords
# This setting effects the score
our $META_KEYWORD_WEIGHT = 20; # a value 1 or above

# Set this to 0 if you DO NOT want to bold and highlight query terms/phrases in titles and descriptions
# Otherwise set it to the HTML color you want the terms to be highlighted
# SECURITY: HTML color values are validated to prevent XSS
our $BOLD_TERMS_BG_COLOR = "#FFFFC9";

# Set this to the HTML color you want the current results in the "navbar" links to be highlighted
# You can always set this to the default background color of your site to avoid highlighting
# SECURITY: HTML color values are validated to prevent XSS
our $BOLD_RESULTS_BG_COLOR = "#FFFEA1";

# You can add your own title for the search form here (HTML okay) or leave it blank with '';
# example $SEARCH_TITLE = '<b>Search the Perl Documentation</b>';
# SECURITY: This content should be pre-sanitized if it contains HTML
our $SEARCH_TITLE = 'No Results Found';

# You can add your own title for the results page. (HTML okay) or leave it blank with '';
# example $RESULTS_TITLE = '<b>Perl Documentation Search Results</b>';
# SECURITY: This content should be pre-sanitized if it contains HTML
our $RESULTS_TITLE = '<div class="content"><h2>Your Search Results</h2></div>';

# You can change the form input name below to avoid editing existing search forms
# SECURITY: Input name is validated in the code
our $FORM_INPUT_NAME = 'terms';	# for form input example <INPUT type="text" name="terms" value="">

# You can change the next and previous links on the resuls page to images that match your site design
# example: <img src="your_next_image.gif" alt="Next" border="0">
our $NEXT = 'Next &rarr;';
our $PREVIOUS = '&larr; Previous';

# Set this to 0 if you DO NOT want to change special characters
# to English equivalents.
our $TRANSLATE_CHARACTERS = 0;	# re-index if changing from 0; # edit-help-template

#### END OF CONFIGURATION SETTINGS ###############################################################
#### You do not have to edit below unless you want to ############################################

# SECURITY: Secure default file paths with proper restrictions
our $DATABASE_DIR = $KSEARCH_DIR.'database/';
our $DATABASEFILE = $DATABASE_DIR.'database.txt';
our $F_FILE_DB_FILE = $DATABASE_DIR.'files';
our $F_SIZE_DB_FILE = $DATABASE_DIR.'files_size';
our $F_DATE_DB_FILE = $DATABASE_DIR.'files_date';
our $F_TERMCOUNT_DB_FILE = $DATABASE_DIR.'files_termcount';
our $DESCRIPTIONS_DB_FILE = $DATABASE_DIR.'descriptions';
our $TITLES_DB_FILE = $DATABASE_DIR.'titles';
our $FILENAMES_DB_FILE = $DATABASE_DIR.'filenames';
our $TERMS_DB_FILE = $DATABASE_DIR.'terms';
our $CONTENTS_DB_FILE = $DATABASE_DIR.'contents';
our $ALT_TEXT_DB_FILE = $DATABASE_DIR.'alt_text';
our $LINKS_DB_FILE = $DATABASE_DIR.'links';
our $META_DESCRIPTION_DB_FILE = $DATABASE_DIR.'meta_description';
our $META_KEYWORD_DB_FILE = $DATABASE_DIR.'meta_keyword';
our $META_AUTHOR_DB_FILE = $DATABASE_DIR.'meta_author';
our $CONFIGURATION_DIR = $KSEARCH_DIR.'configuration/';
our $IGNORE_FILES_FILE = $CONFIGURATION_DIR.'ignore_files.txt';
our $IGNORE_TERMS_FILE = $CONFIGURATION_DIR.'stop_terms.txt';
our $HELP_FILE = $KSEARCH_DIR.'search_tips.html';
our $LOG_FILE = $KSEARCH_DIR.'log.txt';
our $TEMPLATE_DIR = $KSEARCH_DIR.'templates/';
our $KSEARCH_TEMPLATE = $TEMPLATE_DIR.'search.html';
our $FORM_LINK = '<a href="#form" alt="To Search Form" title="To Search Form" onclick="document.search.'.$FORM_INPUT_NAME.'.focus()">Form</a>';
our $SPEED_TIP_TIME = 5;	# time required to get a tip to increase search speed
our $VERSION = "1.7 - Modernized";

# SECURITY: Ensure this file returns true for proper inclusion
1;