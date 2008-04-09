%define name lastfm-player
%define oname player
%define version 1.4.2.58240
%define rel 1

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
Patch0: http://www.mehercule.net/lastfm/00_build-fixes.diff
Patch1: http://www.mehercule.net/lastfm/01_translations.diff
Patch2:	02_tray-icon-size.diff
Patch3: http://www.mehercule.net/lastfm/03_no-scrobble-directories.diff
Patch5: http://mehercule.net/lastfm/05_tray-volume.diff
Patch7:	http://www.mehercule.net/lastfm/no-fingerprint.diff
Patch8:	http://www.mehercule.net/lastfm/alsa-qdebug.diff
Patch9:	09_set-locale.diff
Patch10: http://www.mehercule.net/lastfm/10_save-window-states.diff
Patch11: http://www.mehercule.net/lastfm/check-soundcard-errors.diff
Patch20: http://www.mehercule.net/lastfm/gcc-4.3.patch
Patch52: 52_browser-select.diff

License: GPL
Group: Sound
Url: http://www.last.fm/tools/downloads/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: qt4-devel >= 2:4.3.0 qt4-linguist
BuildRequires: libalsa-devel
#gw ATM not needed on Linux
#BuildRequires: fftw3-devel libsamplerate-devel
BuildRequires: libgpod-devel
BuildRequires: libmad-devel
Provides: player
Obsoletes: player

%description
This is the custom radio player program for last.fm, formerly known as
audioscrobbler.com.

%prep
%setup -q -a 1 -n last.fm-%version
%patch -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch5 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch20 -p1
%patch52 -p1

bzcat %{SOURCE2} | tar -C bin/data/icons -xf - 

chmod -R +r .
perl -pi -e "s|\r\n|\n|" ChangeLog

%build
%{qt4dir}/bin/qmake -config release
make CXX="g++ -fPIC"

cd i18n
%{qt4dir}/bin/lrelease *.ts
mkdir -p ../bin/data/i18n
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
Name=Last.FM Player
Comment=Play the last.fm internet radio
Exec=%name %U
Icon=lastfm
Terminal=false
Type=Application
StartupNotify=true
Categories=Qt;AudioVideo;Audio;Player;
EOF

mkdir -p %buildroot%_datadir/icons
cp -r icons/crystalsvg %buildroot%_datadir/icons/hicolor
find %buildroot -name .svn |xargs rm -rf

rm -f %buildroot%_libdir/%name/*.{lib,dylib}

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
