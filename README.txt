KSEARCH VERSION 1.7 - MODERNIZED & SECURED (2025)

GNU GENERAL PUBLIC LICENSE (v3 or later): ==
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Original project:
    KSearch v1.6 (2012) — https://web.archive.org/web/20130805115023/http://www.ksearch.info/
    Additional resources and documentation via Wayback Machine links in this README.

Modernization & Security Updates (C) 2025 Van Isle Web Solutions
Parts of this script are Copyright:
    www.perlfect.com (C)2000 N.Moraitakis & G.Zervas. All rights reserved
	
=========================================================================================================
== MODERNIZATION SUMMARY: ==
	This version has been completely modernized and secured for 2025 deployment:
	
	✅ CRITICAL SECURITY FIXES APPLIED:
	   • Command injection prevention (PDF processing)
	   • Path traversal protection (file access)
	   • Cross-site scripting (XSS) prevention
	   • Enhanced input validation and authentication
	   
	✅ MODERN PERL COMPATIBILITY:
	   • Compatible with Perl 5.38+ and current versions
	   • Updated deprecated syntax and practices
	   • Added strict/warnings throughout codebase
	   
	✅ IMPROVED USER EXPERIENCE:
	   • Modern HTML5 responsive design
	   • Mobile-friendly interface
	   • Accessibility improvements
	   • Enhanced search form rebuilt from broken Markdown
	   • Responsive CSS with mobile-first design
       • Dark mode and accessibility support
	
	For troubleshooting information read the attached search_tips.html file and/or 
	visit our Discussion Forum sites at: https://web.archive.org/web/20130805115023/http://www.ksearch.info/
==============================================================================
==============================================================================

== FRESH INSTALLATION INSTRUCTIONS: ==
	Seven steps, approximately 10 minutes.

You will need a text editor, FTP/SSH access to your server, and basic command line knowledge.

== SYSTEM REQUIREMENTS: ==
	• Web server with Perl 5.20+ (Perl 5.38+ recommended)
	• CGI.pm module (may need separate installation on newer systems)
	• Write permissions for database directory
	• Optional: PDF indexing requires pdftotext (Xpdf)

== INSTALLATION STEPS: ==

1.	VERIFY PERL AND CGI MODULE:
		Test if CGI.pm is available:
		perl -MCGI -e "print 'CGI.pm version: ', \$CGI::VERSION, \"\n\""
		
		If you get an error, install CGI.pm:
		cpan CGI
		OR
		apt-get install libcgi-pm-perl  (Ubuntu/Debian)
		OR 
		yum install perl-CGI  (CentOS/RHEL)

2.	CREATE DIRECTORY STRUCTURE:
		/your-website/search/
		├── ksearch.cgi
		├── indexer.cgi  
		├── indexer.pl
		├── search_form.html
		├── search_tips.html
		├── ks_images/
		│   ├── KSlogo.gif
		│   ├── style.css (modernized responsive version)
		│   └── [other image files]
		├── configuration/
		│   ├── configuration.pl
		│   ├── ignore_files.txt
		│   └── stop_terms.txt
		├── templates/
		│   └── search.html
		└── database/
		    └── [empty directory - files created automatically]

3.	CONFIGURE SETTINGS:
		Edit search/configuration/configuration.pl
		
		CRITICAL - Update these paths to match your server:
		$INDEXER_START = '/full/path/to/your/website/';
		$BASE_URL = 'https://www.yourdomain.com/';
		$SEARCH_URL = "https://www.yourdomain.com/search/ksearch.cgi";
		$KSEARCH_DIR = '/full/path/to/search/directory/';
		
		SECURITY - Set a strong password:
		$PASSWORD = "Use-A-Very-Strong-Password-Here-123!";
		
		SECURITY - Update valid referers:
		@VALID_REFERERS = ("https://www.yourdomain.com", "http://www.yourdomain.com");

4.	SET FILE PERMISSIONS:
		chmod 755 ksearch.cgi
		chmod 755 indexer.cgi
		chmod 755 indexer.pl
		chmod 644 configuration/configuration.pl
		chmod 644 templates/search.html
		chmod 644 search_form.html
		chmod 644 search_tips.html
		chmod 644 ks_images/*
		chmod 700 database/
		chmod 600 configuration/ignore_files.txt
		chmod 600 configuration/stop_terms.txt

5.	CREATE BASIC CONFIGURATION FILES:
		
		Create configuration/ignore_files.txt (files to skip during indexing):
		# Files and directories to ignore during indexing
		# One pattern per line, wildcards (*) allowed
		*.bak
		*.tmp
		admin/
		private/
		some-file.html
		some-file.php
		
		Create configuration/stop_terms.txt (common words to ignore):
		# Common words to ignore in searches
		the
		and
		or
		but
		in
		on
		at
		to
		for
		of
		with
		by

6.	RUN THE INDEXER:
		Method A - Web Interface (Recommended for first-time):
		• Open browser: https://www.yourdomain.com/search/indexer.cgi
		• Enter the password you set in step 3
		• Wait for indexing to complete (time depends on site size)
		
		Method B - Command Line:
		• SSH to your server
		• cd /path/to/search/directory/
		• perl indexer.pl
		
		The indexer will:
		• Scan all files with configured extensions
		• Extract text content and metadata
		• Build search database files
		• Report statistics when complete
		
		If the indexer.cgi call doesn't work and ends prematurely you will need to contact your host and get the timeout limits raised.
		perl run_indexer.pl

7.	TEST THE INSTALLATION:
		• Visit: https://www.yourdomain.com/search/search_form.html
		• Perform test searches with known content
		• Verify results appear correctly
		• Test advanced search options (phrases, boolean operators)
		
		If you encounter issues, check:
		• Web server error logs
		• File permissions are correct
		• Paths in configuration.pl are accurate
		• CGI.pm module is properly installed

== UPGRADING FROM LAST CURRENT KSEARCH 1.6: ==

If upgrading from the last current 2011 version:

1.	BACKUP YOUR CURRENT INSTALLATION:
		cp -r /path/to/current/ksearch /path/to/ksearch-backup-$(date +%Y%m%d)

2.	REPLACE FILES:
		Replace these files with modernized versions:
		• ksearch.cgi
		• indexer.cgi
		• indexer.pl
		• configuration/configuration.pl
		• search.html (in templates/)
		• search_form.html
		• search_tips.html

3.	UPDATE CONFIGURATION:
		• Edit configuration/configuration.pl with your existing settings
		• Add strong password (now required)
		• Update @VALID_REFERERS to include HTTPS

4.	VERIFY CGI.PM AVAILABILITY:
		• Test: perl -MCGI -e "print 'OK'"
		• Install if needed: cpan CGI

5.	RE-INDEX YOUR SITE:
		• Your existing database will work but re-indexing is recommended
		• Use indexer.cgi or indexer.pl to rebuild search database

== SECURITY FEATURES (NEW): ==

This modernized version includes comprehensive security protections:

	• INPUT VALIDATION: All user inputs are validated and sanitized
	• XSS PREVENTION: HTML output is properly encoded
	• PATH PROTECTION: Directory traversal attacks prevented
	• COMMAND INJECTION: Shell commands secured (PDF processing)
	• AUTHENTICATION: Enhanced password validation for admin access
	• SECURE DEFAULTS: Conservative settings for production use

== RESPONSIVE DESIGN FEATURES (NEW): ==

This modernized version includes comprehensive responsive design:

	- MOBILE-FIRST: Optimized for phones, tablets, and desktops
	- MODERN CSS: Flexbox, Grid, and current web standards
	- ACCESSIBILITY: Keyboard navigation, high contrast, reduced motion support
	- DARK MODE: Automatic detection and appropriate styling
	- TOUCH-FRIENDLY: Larger buttons and form elements for mobile devices
	- PRINT SUPPORT: Clean printing layouts for documentation

== TROUBLESHOOTING: ==

Common Issues:

	ISSUE: "CGI module not found" error
	SOLUTION: Install CGI.pm: cpan CGI

	ISSUE: "Cannot open database file" error  
	SOLUTION: Check database/ directory permissions (should be 700)

	ISSUE: Indexer shows "Authentication error"
	SOLUTION: Verify password in configuration.pl matches what you're entering

	ISSUE: Search returns no results
	SOLUTION: Ensure indexing completed successfully, check file extensions

	ISSUE: "Bad Referer" error on indexer
	SOLUTION: Update @VALID_REFERERS in configuration.pl

	ISSUE: Permission denied errors
	SOLUTION: Verify all file permissions per step 4 above
	
	ISSUE: Styling looks broken or old-fashioned
	SOLUTION: Ensure ks_images/style.css is the modernized version (v1.7)
			  Clear browser cache and refresh page

	ISSUE: Mobile/responsive layout not working
	SOLUTION: Verify modernized style.css is in place, check viewport meta tag

== PERFORMANCE TIPS: ==

	• Set $SAVE_CONTENT = 1 for 5-20x faster searches (uses more disk space)
	• Use flat file database ($USE_DBM = 0) for better reliability
	• Increase $MIN_TERM_LENGTH to reduce noise in search results
	• Regular re-indexing keeps search results current
	• Monitor search_log.txt for popular queries and optimize accordingly

== PRIVACY & LOGGING: ==

	• Search queries are logged for system administration (IP, query, results)
	• No personal information stored beyond IP addresses
	• Log file location: $LOG_SEARCH setting in configuration.pl
	• Consider log rotation for long-term deployments

== ADVANCED FEATURES: ==

All original KSearch features are preserved and enhanced:

	• Boolean search operators (+required, -excluded terms)
	• Phrase searching with quotes ("exact phrase")
	• Wildcard searches (term* matches variations)
	• Weighted scoring (<weight>term for custom relevance)
	• Multiple content types (body, title, meta tags, links, URLs)
	• Customizable result display and sorting options
	• Search within results functionality
	• PDF content indexing (optional, requires pdftotext)
	• Responsive design that works on all devices (phones, tablets, desktops)
	• Modern CSS with accessibility and dark mode support
	• Added "Exact Match" option to eliminate using double quotes in search terms

== FUTURE ENHANCEMENT NOTES: ==

For advanced features like faceted search, analytics, or modern web frameworks:
	• Current version provides secure foundation for migration
	• Consider modern frameworks (Plack/PSGI) for complex enhancements  
	• Database backends (PostgreSQL, MySQL) for advanced analytics
	• Search engines (Elasticsearch, Solr) for enterprise features

== SUPPORT: ==

	For questions specific to this modernized version:
	• Review search_tips.html for detailed usage instructions
	• Check file permissions and configuration settings
	• Verify CGI.pm module installation
	
	For general KSearch support:
	• Original documentation: https://web.archive.org/web/20130805115023/http://www.ksearch.info/
	• Community forum: https://web.archive.org/web/20130806170710/http://support.ksearch.info/

== VERSION HISTORY: ==

	v1.6 (2011): Last current release
	v1.7-Modernized (2025): 
		• Security fixes and modernization
		• Perl 5.38+ compatibility  
		• HTML5 responsive design
		• Enhanced input validation
		• Modern web standards compliance

==============================================================================

Installation complete! Your modernized KSearch is ready for secure, reliable operation.