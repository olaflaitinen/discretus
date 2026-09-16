@ECHO OFF
REM Documentation build helper for Windows.
REM
REM The Unix Makefile next to this file and this batch script expose the same
REM targets, so that a contributor on either platform runs the same build the
REM continuous integration pipeline runs.
REM
REM   make html        build the HTML site into _build\html
REM   make dirhtml     build the HTML site with one directory per page
REM   make latexpdf    build the PDF through pdflatex
REM   make doctest     execute every example in the documentation
REM   make coverage    report the public objects with no reference entry
REM   make linkcheck   verify the external addresses
REM   make strict      build HTML with warnings treated as errors
REM   make serve       build and then serve the site on port 8000
REM   make clean       remove the build directory

pushd %~dp0

REM Command line arguments may override any of these.
IF "%SPHINXBUILD%" == "" (
	SET SPHINXBUILD=sphinx-build
)
SET SOURCEDIR=.
SET BUILDDIR=_build

REM Fail early with an actionable message when the toolchain is missing,
REM rather than with an opaque command not found error.
%SPHINXBUILD% >NUL 2>NUL
IF ERRORLEVEL 9009 (
	ECHO.
	ECHO The 'sphinx-build' command was not found. Install the documentation
	ECHO toolchain first, either with
	ECHO.
	ECHO     pip install -e "..[docs]"
	ECHO.
	ECHO or with
	ECHO.
	ECHO     pip install -r requirements.txt
	ECHO.
	ECHO If Sphinx is installed but not on the path, point the SPHINXBUILD
	ECHO environment variable at the full path of the executable. See also
	ECHO https://www.sphinx-doc.org/
	ECHO.
	EXIT /B 1
)

IF "%1" == "" GOTO help
IF "%1" == "help" GOTO help
IF "%1" == "strict" GOTO strict
IF "%1" == "serve" GOTO serve
IF "%1" == "clean" GOTO clean

REM Any other target is passed straight through to the build, which keeps
REM this script working when a new builder is added upstream.
%SPHINXBUILD% -M %1 "%SOURCEDIR%" "%BUILDDIR%" %SPHINXOPTS% %O%
GOTO end

:help
%SPHINXBUILD% -M help "%SOURCEDIR%" "%BUILDDIR%" %SPHINXOPTS% %O%
ECHO.
ECHO Additional targets provided by this script:
ECHO.
ECHO   strict    build HTML with warnings treated as errors
ECHO   serve     build HTML and serve it on http://localhost:8000
ECHO   clean     remove the build directory
GOTO end

:strict
REM The same invocation the release check uses. The keep going flag reports
REM every warning rather than stopping at the first one, which makes a
REM documentation fix a single pass instead of several.
%SPHINXBUILD% -b html -W --keep-going "%SOURCEDIR%" "%BUILDDIR%\html" %SPHINXOPTS% %O%
GOTO end

:serve
%SPHINXBUILD% -b html "%SOURCEDIR%" "%BUILDDIR%\html" %SPHINXOPTS% %O%
IF ERRORLEVEL 1 GOTO end
ECHO.
ECHO Serving the documentation on http://localhost:8000
ECHO Press Ctrl+C to stop.
python -m http.server 8000 --directory "%BUILDDIR%\html"
GOTO end

:clean
IF EXIST "%BUILDDIR%" (
	RMDIR /S /Q "%BUILDDIR%"
	ECHO Removed %BUILDDIR%
) ELSE (
	ECHO Nothing to clean.
)
GOTO end

:end
popd
