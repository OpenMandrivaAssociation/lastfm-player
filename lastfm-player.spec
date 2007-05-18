%define name lastfm-player
%define oname player
%define version 1.1.3
%define rel 2

Summary: Last.fm web radio player
Name: %{name}
Version: %{version}
Release: %mkrel %rel
Epoch: 1
# svn://svn.audioscrobbler.net/client
Source0: http://static.last.fm/client/Linux/last.fm-%version.src.tar.bz2
Source1: lastfm-icons.tar.bz2
Source2: trayicons22.tar.bz2
# gw these patches come from the unofficial Debian package at:
# http://mehercule.net/staticpages/index.php/lastfm
# fix user path
Patch0:  last.fm-1.1.3-01_dirpaths.diff
# Don't build iTunes related stuff
Patch2:  last.fm-1.1.3-02_noitunes.diff
# Single Click in tray icon shows/hides the main window
Patch3:  last.fm-1.1.3-10_tray.diff
# Increase max history items from 9 to 100 
Patch4:  last.fm-1.1.3-11_history.diff
# Add love and ban items to Recently Played context menu
Patch5:  last.fm-1.1.3-12_loveban.diff
# Use a new alsaaudio plugin based on xmms
Patch6:  last.fm-1.1.3-13_alsa.diff
# Always show the timebar and song countdown
Patch7:  lastfm-1.0.9.6-14_timebar.diff
# Possible scrobble fix. We need to send the "disable scrobbling" signal 
# just a wee bit later
Patch8:  lastfm-1.0.9.6-15_scrobble.diff
# Put an option in Options->Connection that explicitly sets which browser
# the client uses + Mdv usage of www-browser
Patch9:  last.fm-1.1.3-16_select-browser.diff
# Fix a few memory leaks that valgrind reported
Patch11: lastfm-1.0.9.6-18_valgrind.diff
# fix another mem leak
Patch12: lastfm-1.0.9.6-19_delete-http.diff
# Don't check or download updates
Patch13: last.fm-1.1.3-20_noupdates.diff
# Fix translation installation
Patch14: last.fm-1.1.3-03_translations.diff
# Add 22x22 icons for tray (modified for Mandriva)
Patch15: last.fm-1.1.3-21_tray-icon-size.diff
License: GPL
Group: Sound
Url: http://www.last.fm/tools/downloads/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: qt4-devel qt4-linguist
BuildRequires: libalsa-devel
Provides: player
Obsoletes: player

%description
This is the custom radio player program for last.fm, formerly known as
audioscrobbler.com.

%prep
%setup -q -a 1 -n last.fm-%version
%patch0 -p1 -b .dirpaths
%patch2 -p1 -b .noitunes
%patch14 -p1 -b .translations
%patch3 -p1 -b .tray
%patch4 -p1 -b .history
%patch5 -p1 -b .loveban
%patch6 -p1 -b .alsa
%patch7 -p1 -b .timebar
%patch8 -p1 -b .scrobble
%patch9 -p1 -b .select-browser
%patch11 -p1 -b .valgrind
%patch12 -p1 -b .delete_http
%patch13 -p1 -b .noupdates
%patch15 -p1 -b .tray-icon-size

bzcat %{SOURCE2} | tar -C bin/data/icons -xf - 

chmod -R +r .
perl -pi -e "s|\r\n|\n|" ChangeLog

%build
%_prefix/lib/qt4/bin/qmake -config release
make CXX="g++ -fPIC"

cd i18n
%_prefix/lib/qt4/bin/lrelease i18n.pro
cp *.qm ../bin/data/i18n
cd ..

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %buildroot{%_bindir,%_libdir/}
cp -r bin %buildroot%_libdir/%name
cat << EOF > %buildroot%_bindir/%name
#!/bin/sh
%_libdir/%name/last.fm \$*
EOF
install -d -m 755 $RPM_BUILD_ROOT%_datadir/services 
cat > $RPM_BUILD_ROOT%_datadir/services/lastfm.protocol << EOF
[Protocol]
 exec=%_bindir/%name "%u"
 protocol=lastfm
 input=none
 output=none
 helper=true
 listing=
 reading=false
 writing=false
 makedir=false
 deleting=false
EOF

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Last.FM Player
Comment=Play the last.fm internet radio
Exec=%name %U
Icon=lastfm
Terminal=false
Type=Application
StartupNotify=true
Categories=AudioVideo;Audio;Player;X-MandrivaLinux-Multimedia-Sound;
EOF

mkdir -p %buildroot%_datadir/icons
cp -r icons/crystalsvg %buildroot%_datadir/icons/hicolor
find %buildroot -name .svn |xargs rm -rf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_menus
%update_icon_cache hicolor

%postun
%clean_menus
%clean_icon_cache hicolor

%files
%defattr(-,root,root)
%doc ChangeLog README
%attr(755,root,root) %_bindir/%name
%_datadir/applications/mandriva-*
%_datadir/icons/hicolor/*/apps/lastfm*
%_libdir/%name
%_datadir/services/lastfm.protocol


