%define name lastfm-player
%define oname player
%define version 1.5.4.26862
%define rel 1

Summary: Last.fm web radio player
Name: %{name}
Version: %{version}
Release: %mkrel %rel
Epoch: 1
#Source0: http://cdn.last.fm/client/src/last.fm-%version.tar.bz2
Source0: http://www.mehercule.net/lastfm/lastfm_%{version}+dfsg.orig.tar.gz
Source1: icons.tar.gz
Source2: trayicons22.tar.bz2
# gw these patches come from the unofficial Debian package at:
# http://mehercule.net/staticpages/index.php/lastfm
#Don't compile portAudio output plugin on Linux.
# And fix build on 64bit Fedora 13
Patch0: build-fixes.diff
# Make sure the binaries only link to the libraries that they need
Patch1: reduce-linkage.diff
# The Linux client does not do fingerprinting, so don't build it. This reduces the client's package dependencies.
Patch3: no-fingerprint-lib.diff
# With a release build, the ALSA output plugin writes noisy messages to the log file. Only make it noisy in a debug build.
Patch4: alsa-uses-qdebug.diff
# Don't segfault: make sure that the audio device is open before we write to it.
Patch5: check-soundcard-errors.diff
# Use 22x22 icons for Linux system tray.
Patch6: tray-icon-size.diff
# Hide the Scrobble Directories group in the options. It's irrelevant on Linux.
Patch7: hide-scrobbledir-option.diff
# Control the volume by spinning the mouse wheel over the system tray icon.
Patch9: tray-volume.diff
# Correctly sets the language when there is no Last.fm.conf file. If you need to change the language after that, you can do so in Tools | Options | Account.
Patch10: set-locale.diff
# Don't re-run the setup dialog each time the program starts
Patch12: set-firstrun-status.diff
# Small style when using Qt >= 4.5
Patch13: qt45.diff
%if %mdvver >= 201010
# Fix some text/icon display issues with Qt >= 4.6
Patch14: qt46.diff
%endif
%if %mdvver >= 201100
# Fix warnings when compiling with Qt >= 4.7
Patch15: qt47.diff
%endif
# Fix up icon installation path for Linux packages
Patch16: dirpaths.diff

# Explicitly select which browser to use. Set it in Tools | Options | Connection.
Patch52: browser-select.diff
#gw fix linking of the ipod plugin
Patch100: fix-linking.patch
License: GPLv2+
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
%setup -q -a 1 -n lastfm-%{version}+dfsg
%apply_patches

bzcat %{SOURCE2} | tar -C bin/data/icons -xf - 

chmod -R +r .
perl -pi -e "s|\r\n|\n|" ChangeLog

%build
%{qt4dir}/bin/qmake -config release
make CXX="g++ -fPIC $(pkg-config --cflags libgpod-1.0)"

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
export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:%_libdir/%name
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
cp -r icons/hicolor %buildroot%_datadir/icons/hicolor
find %buildroot -name .svn |xargs rm -rf

rm -f %buildroot%_libdir/%name/*.{lib,dylib}
#gw the dirpaths patch expects the data files there:
mv %buildroot%_libdir/%name/data %buildroot%_datadir/lastfm


%clean
rm -rf $RPM_BUILD_ROOT

%if %mdkversion < 200900
%post
%update_menus
%update_icon_cache hicolor
%endif

%if %mdkversion < 200900
%postun
%clean_menus
%clean_icon_cache hicolor
%endif

%files
%defattr(-,root,root)
%doc ChangeLog README
%attr(755,root,root) %_bindir/%name
%_datadir/applications/mandriva-*
%_datadir/icons/hicolor/*/apps/lastfm*
%_libdir/%name
%_datadir/lastfm
%_datadir/services/lastfm.protocol
