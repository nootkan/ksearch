#!/usr/bin/perl -w

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

use strict;
use warnings;

my $t0 = time();
use Fcntl;

# Modern Perl compatibility - try CGI module
my $cgi_available = 0;
eval {
    require CGI;
    CGI->import();
    $cgi_available = 1;
};

if (!$cgi_available) {
    die "ERROR: CGI module not found. Please install with: cpan CGI\n";
}

my $query = new CGI;
print $query->header(-type => 'text/html', -charset => 'UTF-8');
$| = 1; # Force output buffering off to prevent timeouts

###### You may have to add the full path to your configuration file below######
###############################################################################
my $configuration_file = './configuration/configuration.pl'; #CONFIGURATION PATH#

# Temporarily disable strict for configuration loading
no strict 'vars';
do $configuration_file or die "Error loading configuration: $!";
use strict 'vars';

# Declare all configuration variables for use with strict
our ($PASSWORD, $USE_DBM, $MAKE_LOG, $META_DESCRIPTION, $META_KEYWORD, $META_AUTHOR);
our ($ALT_TEXT, $LINKS, $PDF_TO_TEXT, $IGNORE_COMMON_TERMS, $SAVE_CONTENT);
our ($LOG_FILE, $KSEARCH_DIR, $MIN_TERM_LENGTH, $DESCRIPTION_LENGTH, $DESCRIPTION_START);
our ($INDEXER_START, $INDEXER_URL, $VERSION, $DATABASEFILE);
our ($F_FILE_DB_FILE, $F_DATE_DB_FILE, $F_SIZE_DB_FILE, $F_TERMCOUNT_DB_FILE);
our ($DESCRIPTIONS_DB_FILE, $TITLES_DB_FILE, $FILENAMES_DB_FILE, $CONTENTS_DB_FILE);
our ($ALT_TEXT_DB_FILE, $META_DESCRIPTION_DB_FILE, $META_KEYWORD_DB_FILE, $META_AUTHOR_DB_FILE);
our ($LINKS_DB_FILE, $IGNORE_TERMS_FILE, $IGNORE_FILES_FILE, $TRANSLATE_CHARACTERS);
our (@FILE_EXTENSIONS, @VALID_REFERERS);

# Declare internal script variables
my $dbminfo = '';
my $stopwords_regex = '';

# Security: Input validation patterns
my $SAFE_FILENAME_PATTERN = qr/^[a-zA-Z0-9_\-\.\/]+$/;
my $SAFE_PASSWORD_PATTERN = qr/^[a-zA-Z0-9_\-\.\@\!\#\$\%\^\&\*]+$/;
my $MAX_PASSWORD_LENGTH = 100;
my $MAX_FILENAME_LENGTH = 500;

# Security: HTML encode output to prevent XSS
sub html_encode {
    my $text = shift || '';
    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/"/&quot;/g;
    $text =~ s/'/&#x27;/g;
    return $text;
}

# Security: Validate file paths to prevent directory traversal
sub validate_file_path {
    my $path = shift || '';
    
    # Allow absolute paths for configuration files and indexer directories
    if ($path =~ /\/(configuration|search|database)\/.*\.(txt|pl)$/ || 
        $path eq $INDEXER_START || 
        index($path, $INDEXER_START) == 0) {
        # This is a configuration file or indexer directory - allow absolute paths
        return '' if $path =~ /\.\./;  # Still no parent directory access
        return '' if length($path) > $MAX_FILENAME_LENGTH;
        return $path;
    }
    
    # Original validation for regular website files (relative to indexer start)
    return '' if $path =~ /\.\./;  # No parent directory access
    return '' if $path =~ /^[\/\\]/;  # No absolute paths for website files
    return '' unless $path =~ $SAFE_FILENAME_PATTERN;
    return '' if length($path) > $MAX_FILENAME_LENGTH;
    return $path;
}

# Security: Validate password input
sub validate_password {
    my $password = shift || '';
    return '' if length($password) > $MAX_PASSWORD_LENGTH;
    return '' unless $password =~ $SAFE_PASSWORD_PATTERN;
    return $password;
}

# Security: Safe shell command execution (for PDF processing)
sub safe_shell_command {
    my ($command, $filename) = @_;
    
    # Validate filename to prevent injection
    return '' unless $filename;
    return '' if $filename =~ /[;&|`\$\(\)<>]/;  # No shell metacharacters
    return '' unless $filename =~ /^[a-zA-Z0-9_\-\.\/]+$/;
    
    # Validate command path
    return '' unless -x $command;
    
    # Use safe execution method
    my $safe_filename = quotemeta($filename);
    my $safe_command = quotemeta($command);
    
    # Execute with controlled environment
    local %ENV = ( PATH => '/usr/bin:/bin' );  # Restricted PATH
    my $result = `$safe_command $safe_filename - 2>/dev/null`;
    
    return $result || '';
}

my ($allterms, $filesizetotal, $file_count);
my @ignore_files;
my %terms; 			#key = terms; value = number of files the term is found in;

my %f_file_db;			#file path
my %f_date_db;			#file modification date
my %f_size_db;			#file size
my %f_termcount_db;		#number of non-space characters in each file
my %descriptions_db; 		#file description
my %titles_db; 			#file title
my %filenames_db;		#file name
my %contents_db;		#file contents

my %alt_text_db;		#alt text
my %meta_description_db;	#meta descriptions
my %meta_keywords_db;		#meta keywords
my %meta_author_db;		#meta authors
my %links_db;			#links

my $htmlfooter=<<HTMLFOOTER;
</font>
</body>
</html>
HTMLFOOTER

if ($query->param("login") eq "indexer") {

my $htmlheader=<<HTMLHEADER;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<head>
<title>KSearch 1.7 Indexer Login</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>

<body>
<font face="Arial" size="2">
HTMLHEADER

print $htmlheader;

validate_page();

# Security: Enhanced password validation
my $input_password = $query->param("pwd") || '';
my $safe_password = validate_password($input_password);

if (!$PASSWORD || !$safe_password || $safe_password ne $PASSWORD) {
	print "<font face=Arial color=red><b>Authentication error.</b></font>";
	print $htmlfooter;
	exit;
}

print "<h4>Please wait until this page is finished loading before closing this window<br />
	or browsing the internet. If the script prematurely terminates, your server<br />
	may have timed out.<br><br>When the indexer completes, the last line should read: Total run time: ....</h4>";

my $dbm_package;
if ($USE_DBM) {
	package AnyDBM_File;
	our @ISA = qw(DB_File GDBM_File SDBM_File ODBM_File NDBM_File) unless @ISA;
	my $dbminfo = '';
	for (@ISA) {
  		if (eval "require $_") {
			$dbminfo .= "\n\nUsing DBM Database: $_...\n\n";
  			if ($_ =~ /[SON]DBM_File/) {
				$USE_DBM = 0;  # Fixed typo: was $USE_DMB
  				$dbminfo .= "Warning: $_ has block size limits.\n";
				$dbminfo .= "If your site exeeds the limit you will receive error message:\n";
				$dbminfo .= "[ dbm store returned -1, errno 28, key \"trap\" at - line 3. ]\n";
				$dbminfo .= "It is highly recommended to use a flat file database by setting \$USE_DBM to 0 in configuration.pl.\n";
				$dbminfo .= "See the README file for details.\n\n";  # Fixed typo: was $dmbinfo
  			}
			print html_encode($dbminfo);
			if ($_ =~ /[SON]DBM_File/) {
				print "<br>\n<br>\nINDEXING WILL CONTINUE IN 10 SECONDS<br>\n";
				sleep 10;
			}
			$dbm_package = $_;
			last;
  		}
	}
	package main;
}

cleanup(); # delete existing db files

my $logterms = '';  # Fixed undefined variable

if ($MAKE_LOG) {
	my $indexmetadesc = $META_DESCRIPTION ? "yes" : "no";
	my $indexmetakeywords = $META_KEYWORD ? "yes" : "no";
	my $indexmetaauthor = $META_AUTHOR ? "yes" : "no";
	my $indexalttext = $ALT_TEXT ? "yes" : "no";
	my $indexlinks = $LINKS ? "yes" : "no";
	my $indexpdf = $PDF_TO_TEXT ? "yes" : "no";
	my $removecommonterms = $IGNORE_COMMON_TERMS ? "yes [cutoff = $IGNORE_COMMON_TERMS percent]" : "no";
	my $indexcontent = $SAVE_CONTENT ? "yes" : "no (warning: search may be very slow for large sites)";
	
	# Security: Validate log file path
	my $safe_log_file = validate_file_path($LOG_FILE);
	if ($safe_log_file) {
		open(LOG,">".$safe_log_file) or (warn "Cannot open log file $safe_log_file: $!");
		print LOG localtime()."\nConfiguration File: $KSEARCH_DIR$configuration_file\n";
		print LOG ($dbminfo || '');
		print LOG "\nINDEXER SETTINGS:\n";
		print LOG "Minimum term length: $MIN_TERM_LENGTH\n";
		print LOG "Description length: $DESCRIPTION_LENGTH\n";
		print LOG "Index meta descriptions: $indexmetadesc\n";
		print LOG "Index meta keywords: $indexmetakeywords\n";
		print LOG "Index meta authors: $indexmetaauthor\n";
		print LOG "Index alternative text: $indexalttext\n";
		print LOG "Index links: $indexlinks\n";
		print LOG "Index PDF files: $indexpdf\n";
		print LOG "Save file contents to database: $indexcontent\n";
		print LOG "Add Common terms to STOP TERMS file: $removecommonterms\n";
		print LOG "Index files with extensions: ".(join " ", @FILE_EXTENSIONS)."\n";
	}
}

if ($USE_DBM) {
	tie %f_file_db, $dbm_package, $F_FILE_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $F_FILE_DB_FILE: $!";
	tie %f_date_db, $dbm_package, $F_DATE_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $F_DATE_DB_FILE: $!";
	tie %f_size_db, $dbm_package, $F_SIZE_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $F_SIZE_DB_FILE: $!";
	tie %f_termcount_db, $dbm_package, $F_TERMCOUNT_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $F_TERMCOUNT_DB_FILE: $!";
	tie %descriptions_db, $dbm_package, $DESCRIPTIONS_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $DESCRIPTIONS_DB_FILE: $!";
	tie %titles_db, $dbm_package, $TITLES_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $TITLES_DB_FILE: $!";
	tie %filenames_db, $dbm_package, $FILENAMES_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $FILENAMES_DB_FILE: $!";
	if ($SAVE_CONTENT) {
		tie %contents_db, $dbm_package, $CONTENTS_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $CONTENTS_DB_FILE: $!";
	}
	if ($ALT_TEXT) {
		tie %alt_text_db, $dbm_package, $ALT_TEXT_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $ALT_TEXT_DB_FILE: $!";
	}
	if ($META_DESCRIPTION) {
		tie %meta_description_db, $dbm_package, $META_DESCRIPTION_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $META_DESCRIPTION_DB_FILE: $!";
	}
	if ($META_KEYWORD) {
		tie %meta_keywords_db, $dbm_package, $META_KEYWORD_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $META_KEYWORD_DB_FILE: $!";
	}
	if ($META_AUTHOR) {
		tie %meta_author_db, $dbm_package, $META_AUTHOR_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $META_AUTHOR_DB_FILE: $!";
	}
	if ($LINKS) {
		tie %links_db, $dbm_package, $LINKS_DB_FILE, O_CREAT|O_RDWR, 0644 or die "Cannot open $LINKS_DB_FILE: $!";
	}
}

push @FILE_EXTENSIONS, 'pdf' if $PDF_TO_TEXT; # if the option to index PDF files is chosen

print "<br>\nLoading files to ignore:<br>\n";
print LOG "\nLoading files to ignore:\n" if ($MAKE_LOG && fileno(LOG));
$| = 1; # Flush output

ignore_files();

print "<br><br>\nUsing stop words file: ".html_encode($IGNORE_TERMS_FILE)."<br>\n";
print LOG "\n\nUsing stop words file: $IGNORE_TERMS_FILE\n" if ($MAKE_LOG && fileno(LOG));
$| = 1; # Flush output

$stopwords_regex = ignore_terms();

print "<br>\nStarting indexer at ".html_encode($INDEXER_START)."<br>\n<br>\n";
print LOG "\nStarting indexer at $INDEXER_START\n\n" if ($MAKE_LOG && fileno(LOG));
$| = 1; # Flush output

# Initialize counters to prevent undefined warnings
$allterms = 0;
$filesizetotal = 0;
$file_count = 0;

if (!$USE_DBM) {
	# Security: Validate database file path
	my $safe_db_file = validate_file_path($DATABASEFILE);
	die "Invalid database file path" unless $safe_db_file;
	open(FILEDB, ">", $safe_db_file) || die "Cannot open database file: $!\n";
}

# Add error handling around the main indexer call
eval {
    indexer($INDEXER_START);
};
if ($@) {
    print "<br><font color='red'><strong>INDEXER ERROR:</strong> " . html_encode($@) . "</font><br>\n";
}

close(FILEDB) if (!$USE_DBM);

# remove COMMON TERMS previously appended to STOP TERMS file
clean_stop_terms();

# append COMMON TERMS to STOP TERMS file if configured to do so
append_common_terms() if $IGNORE_COMMON_TERMS;

print "<br>\n<br>\nFinished: Indexed ".($file_count || 0).' files ('.($filesizetotal || 0).'KB) with '.($allterms || 0)." total terms.<br>\n";
print LOG "\n\nFinished: Indexed ".($file_count || 0).' files ('.($filesizetotal || 0).'KB) with '.($allterms || 0)." total terms.\n" if ($MAKE_LOG && fileno(LOG));

print "Saved information ".$logterms."in logfile:<br>\n ".html_encode($LOG_FILE)."<br>\n<br>\n" if $MAKE_LOG;

my $timediff = time() - $t0;
my $seconds = $timediff % 60;
my $minutes = ($timediff - $seconds) / 60;
if ($minutes >= 1) { $minutes = ($minutes == 1 ? "$minutes minute" : "$minutes minutes"); } else { $minutes = ""; }
$seconds = ($seconds == 1 ? "$seconds second" : "$seconds seconds");
print "Total run time: $minutes $seconds<br>\n";
print LOG "Total run time: $minutes $seconds\n" if ($MAKE_LOG && fileno(LOG));
close (LOG) if ($MAKE_LOG && fileno(LOG));

print $htmlfooter;

} else {

my $html=<<HTMLPAGE;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>KSearch 1.7 Indexer Login</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body>
<form method="post" action="$INDEXER_URL">
<div style="text-align:justify; width:400px; margin:10px auto; padding-top:20px;">
	<table border="0" cellpadding="5" cellspacing="1" width="400">
		<tr><td align="center">
			<font face="Verdana" color="#00CC00" size="4">
				KSearch 1.7 Indexer <img src="ks_images/KSlogo.gif" alt="KSearch 1.7" /><br /><br />
			</font>
		</td></tr>
		<tr><td align="center" bgcolor="#00B852">
			<font face="Verdana" size="2"><br />
				<strong>Password:</strong><br />
				<input type="password" name="pwd" maxlength="100" />
				<input type="hidden" name="login" value="indexer" />
			<br /><br />
				<input type="submit" value="Run Indexer" />
			<br /><br />
			</font>
		</td></tr>
		<tr><td>
			<font face="Arial" size="2">
				<br />
				Refer back to your Configuration file if you receive error messages on the next page. Then 
				click the "back" button in your browser, fix the associated errors, refresh this page, and 
				try again.<br /><br />
				If the indexer prematurely terminates, your server may be 
				set to time out the HTTP request before giving the indexer enough time to complete. If 
				this happens, ask your host service or system administrator to increase the time out setting 
				on the server.				
			</font>
		</td></tr>
	</table>
	<table border="0" cellpadding="2" cellspacing="1" width="400">
		<tr><td align="right">
			<font face="Verdana" size="1">
				KSearch v$VERSION
			</font>
		</td></tr>
	</table>
	<div style="text-align:center; padding-top:30px;" >
		<a href="http://www.kscripts.com/"><img src="ks_images/ks-kscripts.gif" border="0" alt="KScripts Home" /></a> &nbsp; 
		<a href="http://www.kscripts.com/discus/index.php"><img src="ks_images/ks-forum.gif" border="0" alt="KScripts Forum" /></a> &nbsp; 
		<a href="http://validator.w3.org/check?uri=referer"><img src="ks_images/valid_xhtml.gif" border="0" alt="XHTML Valid" /></a>
	</div>
</div>
</form>
</body>
</html>
HTMLPAGE
print $html;
exit;
}

####sub routines###########################################################################

sub indexer {
  my $dir = $_[0];
  my ($file_ref, $file);
  
  # Security: Validate directory path
  my $safe_dir = validate_file_path($dir);
  unless ($safe_dir) {
      return;
  }
  
  # Check if directory exists and is readable
  unless (-d $safe_dir) {
      return;
  }
  
  unless (-r $safe_dir) {
      return;
  }
  
  unless (chdir $safe_dir) {
      return;
  }
  
  unless (opendir(DIR, $safe_dir)) {
      return;
  }
  
  my @dir_contents = readdir DIR;
  closedir(DIR);
  
  my @dirs  = grep {-d and not /^\.{1,2}$/} @dir_contents;
  my @files = grep {-f and /^.+\.(.+)$/ and grep {/^\Q$1\E$/} @FILE_EXTENSIONS} @dir_contents;
  
  print "<br>\nProcessing directory: ".html_encode($dir)."<br>\n";
  print "Found " . scalar(@files) . " files and " . scalar(@dirs) . " subdirectories<br>\n";
  $| = 1; # Flush output
  
  FILE: foreach my $file_name (@files) {
    $file = $dir."/".$file_name;
    $file =~ s/\/\//\//og;
    
    # Security: Validate file path
    my $safe_file = validate_file_path($file);
    unless ($safe_file) {
        next FILE;
    }
    
    foreach my $skip (@ignore_files) {
      # Check if file path contains the ignored directory
      if ($file =~ m/\Q$skip\E/ || $file =~ m/^$skip$/) {
          next FILE;
      }
    }
    
    eval {
        index_file($safe_file);
    };
    if ($@) {
    }
    
    $| = 1; # Flush output after each file
  }
  
  DIR: foreach my $dir_name (@dirs) {
    $file = $dir."/".$dir_name;
    $file =~ s/\/\//\//og;
    
    # Security: Validate directory path
    my $safe_subdir = validate_file_path($file);
    unless ($safe_subdir) {
        next DIR;
    }
    
    foreach my $skip (@ignore_files) {
      # Check if directory path contains the ignored directory  
      if ($file =~ m/\Q$skip\E/ || $file =~ /^$skip$/) {
          next DIR;
      }
    }
    
    eval {
        indexer($safe_subdir);
    };
    if ($@) {
    }
  }
}

sub index_file {
  my $file = $_[0];
  my ($contents, $f_termcount);
  my %totalterms;
  my %term_total;
  
  if($PDF_TO_TEXT && $file =~ m/\.pdf$/i) {	# if the file is a PDF file
    # Security: Enhanced filename validation for PDF processing
    if( $file !~ m/^[\/\\\w.+-]*$/ || $file =~ m/\.\./ || $file =~ m/[;&|`\$\(\)<>]/ ) {
      print "<br>\nIgnoring PDF file '".html_encode($file)."': filename has illegal characters<br>\n<br>\n";
      print LOG "\nIgnoring PDF file '$file': filename has illegal characters\n\n" if ($MAKE_LOG && fileno(LOG));
      return;
    }
    
    # Security: Use safe shell command execution
    $contents = safe_shell_command($PDF_TO_TEXT, $file);
    unless ($contents) {
      print "<br>\nCannot execute PDF processing for '".html_encode($file)."'<br>\nIgnoring PDF file<br>\n<br>\n";
      print LOG "\nCannot execute PDF processing for '$file'\nIgnoring PDF file\n\n" if ($MAKE_LOG && fileno(LOG));
      return;
    }
  } else {
    undef $/;
    unless (open(FILE, '<', $file)) {
        return;
    }
    $contents = <FILE>;
    close(FILE);
    $/ = "\n";
  }

  if (!$contents || $contents =~ /^\s*$/gs) {
      return; 
  } # skip empty files

  ++$file_count; # file reference number
  $f_size_db{$file_count} = int((((stat($file))[7] || 0)/1024)+.5);	# get size of file in kb
  $filesizetotal += $f_size_db{$file_count};			# get total size of all files
  my $update = (stat($file))[9] || 0;	 			# get date of last file modification
  $f_date_db{$file_count} = int($update/8640);
  $update = get_date($update);

  print "Indexed ".html_encode($file)." <br>\n Last Updated: ".html_encode($update)." <br>\n File Size: ".$f_size_db{$file_count}." KB<br>\n";
  print LOG "Indexed $file \n Last Updated: $update \n File Size: $f_size_db{$file_count} KB\n" if ($MAKE_LOG && fileno(LOG));

  $file =~ m/^$INDEXER_START(.*)$/;
  $file = $1 || '';
  $f_file_db{$file_count} = $file;

  if ($file =~ /[\/\\]([^\/\\]+)$/) {
	  $filenames_db{$file_count} = $1;
  } else {
	  $filenames_db{$file_count} = $file;
  }

  # save content if configured to do so, remove html and scripts
  $contents = process_contents($contents, $file_count, $file);

  # Initialize counter for this function
  $f_termcount = 0;

   while ($contents =~ m/\b(\S+)\b/gs) {
    my $term = $1;
    $f_termcount_db{$file_count} += length $term;			# count all non-space characters in file
    $f_termcount++;
    if ($IGNORE_COMMON_TERMS) {						# count terms in file
	    next if $stopwords_regex && $term =~ m/^$stopwords_regex$/io;	# skip stop words
	    if (length $term >= $MIN_TERM_LENGTH && !$term_total{$term}) {	# each term in file if valid
	      $term_total{$term} = undef;
	    }
    }
  }
  $allterms += $f_termcount;					# count all terms in all files
  if ($IGNORE_COMMON_TERMS) {
	  foreach (keys %term_total) {
	    $terms{$_}++;					# count files with each term
	  }
  }

##########################################################################################

 if (!$USE_DBM) {
 	# Save all hash data into flat files with tab delimiter
	my $file_entry = $f_file_db{$file_count} || '';			# file path
	my $filename_entry = $filenames_db{$file_count} || '';		# file name
	my $date_entry = $f_date_db{$file_count} || 0;			#file modification date
	my $size_entry = $f_size_db{$file_count} || 0;			#file size
	my $termcount_entry = $f_termcount_db{$file_count} || 0;		#number of non-space characters in each file
	my $descriptions_entry = $descriptions_db{$file_count} || ''; 	#file description
	my $titles_entry = $titles_db{$file_count} || ''; 			#file title
	my $contents_entry = $contents_db{$file_count} || '';			#file contents
	my $alt_text_entry = $alt_text_db{$file_count} || '';			#alt text
	my $meta_desc_entry = $meta_description_db{$file_count} || '';	#meta descriptions
	my $meta_key_entry = $meta_keywords_db{$file_count} || '';		#meta keywords
	my $meta_auth_entry = $meta_author_db{$file_count} || '';		#meta authors
	my $links_entry = $links_db{$file_count} || '';			#links

	print FILEDB "$file_entry\t$filename_entry\t$date_entry\t$size_entry\t$termcount_entry\t$descriptions_entry\t$titles_entry\t$contents_entry\t$alt_text_entry\t$meta_desc_entry\t$meta_key_entry\t$meta_auth_entry\t$links_entry\n";
}

##########################################################################################
}

sub get_date {  # gets date of last modification
   my $updatetime = $_[0] || 0;
   my @month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
   my ($mday,$mon,$yr) = (localtime($updatetime))[3,4,5];
   $yr += 1900;
   my $date = "$month[$mon] $mday, $yr";
   $date ||= "n/a";
   return $date;
}

sub process_contents {  # process contents
  my ($contents, $file_ref, $filename) = @_;
  $contents ||= '';
  
  if ($ALT_TEXT) {
	my $alt_text = '';
	while ($contents =~ m/\s+alt\s*=\s*[\"\'](.*?)[\"\'][> ]/gis) {
	        $alt_text .= "$1 ";
	}
	$alt_text =~ s/\s+/ /g;
	$alt_text_db{$file_ref} = $alt_text if $alt_text;
  }
  if ($LINKS) {
	my $links = '';
	while ($contents =~ m/<\s*a\s+href\s*=\s*[\"\'](.*?)[\"\'][> ]/gis) {
	        $links .= "$1 ";
	}
	$links =~ s/\s+/ /g;
	$links_db{$file_ref} = $links if $links;
  }
  if ($META_DESCRIPTION) {
  	if ($contents =~ m/<\s*META\s+name\s*=\s*[\"\']?description[\"\']?\s+content\s*=\s*[\"\']?(.*?)[\"\']?\s*>/is) {
		my $meta_descript = $1;
		$meta_descript =~ s/\s+/ /g;
		$meta_description_db{$file_ref} = $meta_descript;
	}
  }
  if ($META_KEYWORD) {
  	if ($contents =~ m/<\s*META\s+name\s*=\s*[\"\']?keywords[\"\']?\s+content\s*=\s*[\"\']?(.*?)[\"\']?\s*>/is) {
		my $meta_key = $1;
		$meta_key =~ s/\s+/ /g;
		$meta_keywords_db{$file_ref} = $meta_key;
	}
  }
  if ($META_AUTHOR) {
  	if ($contents =~ m/<\s*META\s+name\s*=\s*[\"\']?author[\"\']?\s+content\s*=\s*[\"\']?(.*?)[\"\']?\s*>/is) {
		my $meta_aut = $1;
		$meta_aut =~ s/\s+/ /g;
		$meta_author_db{$file_ref} = $meta_aut;
	}
  }
  $contents =~ s/(<\s*script[^>]*>.*?<\s*\/script\s*>)|(<\s*style[^>]*>.*?<\s*\/style\s*>)/ /gsi;	# remove scripts and styles

  record_description($file_ref, $filename, $contents);	# record titles and descriptions

  $contents =~ s/<\s*TITLE\s*>\s*(.*?)\s*<\s*\/TITLE\s*>//gsi;		# remove title
  $contents =~ s/<\s*!--nosearch--\s*>\s*(.*?)\s*<\s*!--\/nosearch--\s*>//gsi;		# remove NOSEARCH section
  $contents =~ s/<digit>|<code>|<\/code>//gsi;
  $contents =~ s/(<[^>]*>)|(&nbsp;)|(&#160;)/ /gs;		# remove html poorly
  $contents = translate_characters($contents);			# translate ISO Latin special characters to English approximations
  $contents =~ s/^\s+//gs;
  $contents =~ s/\s+$//gs;
  $contents =~ s/\s+/ /gs;

  if ($SAVE_CONTENT) {				# may use a lot of disk space (for hybrid data structure)
	$contents_db{$file_ref} = $contents;	# saves cleaned file content for faster searching
	if ($USE_DBM) {	# use DBM if no size limits
		print " Saved file contents to DBM database<br>\n<br>\n";
		print LOG " Saved file contents to DBM database\n\n" if ($MAKE_LOG && fileno(LOG));
	} else {
		print " Saved file contents to Flat File database<br>\n<br>\n";
		print LOG " Saved file contents to Flat File database\n\n" if ($MAKE_LOG && fileno(LOG));
	}
  } else {
	print "<br>\n";
	print LOG "\n" if ($MAKE_LOG && fileno(LOG));
  }
  return lc $contents;
}

sub record_description {  # record descriptions and titles
  my ($file_ref, $file, $contents) = @_;
  my ($description, $title);
  my @temparray;
  $contents ||= '';
  $file ||= '';
  
  if ($contents =~ m/<\s*BODY.*?>(.*)<\s*\/BODY\s*>/si) {
	$description = $1;
  } else {
	$description = $contents;
  }
  $description =~ s/<\s*TITLE\s*>\s*(.*?)\s*<\s*\/TITLE\s*>//gsi;	# remove title
  $description =~ s/<digit>|<code>|<\/code>//gsi;
  $description =~ s/(<[^>]*>)|(&nbsp;)|(&#160;)/ /gs;			# remove html poorly
  $description = translate_characters($description);			# translate ISO Latin special characters to English approximations
  $description =~ s/^\s+//gs;
  $description =~ s/\s+$//gs;
  $description =~ s/\s+/ /gs;

  @temparray = split " ", $description;
  my $start_desc = $DESCRIPTION_START;
  my $end_desc = $DESCRIPTION_START + $DESCRIPTION_LENGTH;
  $start_desc = ($end_desc > scalar@temparray ? 0 : $DESCRIPTION_START);
  $description = join " ", @temparray[$start_desc..$end_desc];
  $description = '...'.$description if $start_desc;
  $description =~ s/\s+$//;
  $descriptions_db{$file_ref} = $description.'...';

  if ($contents =~ m/<\s*TITLE\s*>\s*(.*?)\s*<\s*\/TITLE\s*>/is) {
	  $title = $1;
  }
  $file =~ s/^.*\/([^\/]+)$/$1/g;
  $title ||= $file;
  $title =~ s/(<[^>]*>)|(&nbsp;)|(&#160;)/ /gs;	# remove html poorly
  $title =~ s/\s+/ /gs;				# remove spaces
  $title = translate_characters($title);	# translate ISO Latin special characters to English approximations
  $titles_db{$file_ref} = $title;
  print " Title: ".html_encode($title)."<br>\n Description: ".html_encode($description)."<br>\n";
  print LOG " Title: $title\n Description: $description\n" if ($MAKE_LOG && fileno(LOG));
}

sub ignore_files {
  my @list;
  # Security: Validate ignore files path
  my $safe_ignore_file = validate_file_path($IGNORE_FILES_FILE);
  if ($safe_ignore_file && -e $safe_ignore_file) {
    open (FILE, '<', $safe_ignore_file) or (warn "Cannot open $safe_ignore_file: $!\n");
    while (<FILE>) {
      chomp;
      $_ =~ s/\r//g;
      $_ =~ s/\#.*$//g;
      $_ =~ s/^\s+|\s+$//g;  # Remove only leading/trailing whitespace
      next if /^\s*$/;
      push @list, html_encode($_)."<br>\n";
      # Only escape patterns with wildcards, preserve simple filenames
      if ($_ =~ /\*/) {
          $_ = quotemeta($_);
          $_ =~ s/\\\*/\.\*/g;
      }
      push @ignore_files, $_;
    }
    close (FILE);
    if (scalar@list > 0) { 
      print @list; 
      print LOG map { s/<[^>]*>//g; $_ } @list if ($MAKE_LOG && fileno(LOG));  # Remove HTML encoding for log
    } else { 
      print "List is empty<br>\n<br>\n"; 
      print LOG "List is empty\n\n" if ($MAKE_LOG && fileno(LOG));
    }
  } else {
    print STDERR "Warning: Can't find $IGNORE_FILES_FILE.\n";
  }
}

sub ignore_terms {
  my @stopwords;
  my $stopwords_regex = '';
  
  # Security: Validate ignore terms file path
  my $safe_ignore_terms = validate_file_path($IGNORE_TERMS_FILE);
  if ($safe_ignore_terms) {
    open (FILE, '<', $safe_ignore_terms) or (warn "Cannot open $safe_ignore_terms: $!");
    while (<FILE>) {
      chomp;
      last if /\#DO NOT EDIT/;
      $_ =~ s/\#.*$//g;
      $_ =~ s/\s//g;
      next if /^\s*$/;
      $_ =~ s/([^\w\s])/\\$1/g;
      push @stopwords, $_;
    }
    close(FILE);
    $stopwords_regex = '(' . join('|', @stopwords) . ')' if @stopwords;
  } else {
  }
  return $stopwords_regex;
}

sub cleanup {
  print "Deleting existing db files:<br>\n";

    foreach (($CONTENTS_DB_FILE, $F_TERMCOUNT_DB_FILE, $F_FILE_DB_FILE, $F_DATE_DB_FILE, $F_SIZE_DB_FILE, $DESCRIPTIONS_DB_FILE, $TITLES_DB_FILE, $ALT_TEXT_DB_FILE, $META_DESCRIPTION_DB_FILE, $META_KEYWORD_DB_FILE, $META_AUTHOR_DB_FILE, $LINKS_DB_FILE, $FILENAMES_DB_FILE))
{
    if (-e $_.'.pag') {
      print "\t ".html_encode($_)."<br>\n";
      unlink $_.'.pag' or (warn "Cannot unlink $_: $!");
    }
    if (-e $_) {
      print "\t ".html_encode($_)."<br>\n";
      unlink $_ or (warn "Cannot unlink $_: $!");
    }
  }
    foreach (($CONTENTS_DB_FILE, $F_TERMCOUNT_DB_FILE, $F_FILE_DB_FILE, $F_DATE_DB_FILE, $F_SIZE_DB_FILE, $DESCRIPTIONS_DB_FILE, $TITLES_DB_FILE, $ALT_TEXT_DB_FILE, $META_DESCRIPTION_DB_FILE, $META_KEYWORD_DB_FILE, $META_AUTHOR_DB_FILE, $LINKS_DB_FILE, $FILENAMES_DB_FILE))
{
    if (-e $_.'.dir') {
      print "\t ".html_encode($_)."<br>\n";
      unlink $_.'.dir' or (warn "Cannot unlink $_: $!");
    }
  }
}

sub append_common_terms { # appends common terms to STOP TERMS file
	my (@common_terms, @stop_terms, @stop_terms_copy);
	while (my ($term,$files) = each %terms) {
		if ($files > ($IGNORE_COMMON_TERMS/100 * $file_count)) {
			push @common_terms, $term;
		}
	}
	if (@common_terms) {
		# Security: Validate stop terms file path
		my $safe_stop_terms = validate_file_path($IGNORE_TERMS_FILE);
		if ($safe_stop_terms) {
			open(STOPTERMS,'>>'.$safe_stop_terms) || die "Cannot open $safe_stop_terms: $!";
			print STOPTERMS "\n#DO NOT EDIT: Terms present in over $IGNORE_COMMON_TERMS percent of all files\n";
			foreach my $term (@common_terms) {
				print html_encode($term)."<br>\n";
				print LOG "$term\n" if ($MAKE_LOG && fileno(LOG));
				print STOPTERMS "$term\n";
			}
			print "<br>\nThe above terms were present in over $IGNORE_COMMON_TERMS percent of all files and were added to your STOP TERMS file:<br>\n ".html_encode($IGNORE_TERMS_FILE);
			print LOG "\nThe above terms were added to your STOP TERMS file:\n $IGNORE_TERMS_FILE" if ($MAKE_LOG && fileno(LOG));
			close (STOPTERMS);
		}
	} else {
		print "<br>\nNo common terms were present in over $IGNORE_COMMON_TERMS percent of all files";
		print LOG "\nNo common terms were present in over $IGNORE_COMMON_TERMS percent of all files" if ($MAKE_LOG && fileno(LOG));
	}
}

sub clean_stop_terms {
	my (@stop_terms, @stop_terms_copy);
	# Security: Validate stop terms file path
	my $safe_stop_terms = validate_file_path($IGNORE_TERMS_FILE);
	return unless $safe_stop_terms;
	
	open(STOPTERMS, '<', $safe_stop_terms) || die "Cannot open $safe_stop_terms: $!";
	@stop_terms = <STOPTERMS>;
        close (STOPTERMS);
        foreach (@stop_terms) {
		last if /#DO NOT EDIT/;
		next if /^\s*$/;
		push @stop_terms_copy, $_;
	}
	open(STOPTERMS, '>', $safe_stop_terms) || die "Cannot open $safe_stop_terms: $!";
        print STOPTERMS @stop_terms_copy;
	close(STOPTERMS);
}

sub translate_characters {
	# From http://www.utoronto.ca/webdocs/HTMLdocs/NewHTML/iso_table.html
	my $translated_term = $_[0] || '';

	if (!$TRANSLATE_CHARACTERS) { return $translated_term; }

	$translated_term =~ s/&(.?)(acute|grave|circ|uml|tilde);/$1/gs;
	$translated_term =~ s/(&#247|&(nbsp|divide);)/ /og;
	$translated_term =~ s/(&#(192|193|194|195|196|197|224|225|226|227|228|229|230);|À|Á|Â|Ã|Ä|Å|à|á|â|ã|ä|æ|å|&(.ring|aelig);)/a/og;
	$translated_term =~ s/(&#223;|ß|&szlig;)/b/og;
	$translated_term =~ s/(&#(199|231);|Ç|ç|&.cedil;)/c/og;
	$translated_term =~ s/(&#(198|200|201|202|203|232|233|234|235);|Æ|È|É|Ê|Ë|è|é|ê|ë|&AElig;)/e/og;
	$translated_term =~ s/(&#(204|205|206|207|236|238|239);|Ì|Í|Î|Ï|ì|í|î|ï)/i/og;
	$translated_term =~ s/(&#(209|241);|ñ|Ñ)/n/og;
	$translated_term =~ s/(&#(216|210|211|212|213|214|240|242|243|244|245|246|248);|Ø|Ò|Ó|Ô|Õ|Ö|ð|ò|ó|ô|õ|ö|ø|&(.slash|eth);)/o/og;
	$translated_term =~ s/(&#(217|218|219|220|249|250|251|252);|Ù|Ú|Û|Ü|ù|ú|û|ü)/u/og;
	$translated_term =~ s/(&#(222|254);|Þ|þ|&thorn;)/p/og;
	$translated_term =~ s/(&#215;|×|&times;)/x/og;
	$translated_term =~ s/(&#(221|253);|Ý|ý)/y/og;

	$translated_term =~ s/(&#34|&quot);/"/og;
	$translated_term =~ s/&#35;/#/og;
	$translated_term =~ s/&#36;/\$/og;
	$translated_term =~ s/&#37;/\%/og;
	$translated_term =~ s/(&#38|&amp);/&/og;
        $translated_term =~ s/(<|&#60;)/&lt;/og;
        $translated_term =~ s/(>|&#62;)/&gt;/og;
	return $translated_term;
}

sub validate_page {
	my ($okay, $referer);
	if (!@VALID_REFERERS) {return;}
	$referer = lc($ENV{'HTTP_REFERER'} || '');
	foreach my $ref (@VALID_REFERERS) {
		if ($referer =~ /^$ref/i) { $okay = 1; }
	}
	if (!$okay) {
		print "<font face=verdana color=red><b>Bad Referer.</b></font>";
		print $htmlfooter;
		exit;
	}
}