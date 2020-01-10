%define name lastfm-player
%define oname player
%define version 1.5.4.27091

Summary: Last.fm web radio player
Name: %{name}
Version: %{version}
Release: %mkrel 3
Epoch: 1
#gw fetched from svn://svn.audioscrobbler.net/clientside/Last.fm/tags/1.5.4
#with useless binaries and other files removed (just like the Debian folks
#did with their dfsg tarballs):
#rm -rf bin/*dll bin/sqldrivers/ bin/Microsoft* bin/*lib res/libsamplerate/ res/mad/ src/Twiddly/iTunesCOMAPI/ src/breakpad/external/ src/libFingerprint/libs/ src/libUnicorn/z* src/mediadevices/ipod/include/ src/output/RtAudio/dsound/ src/output/portAudio/PortAudio/
Source0: http://cdn.last.fm/client/src/lastfm-%version.tar.xz
#Source0: http://www.mehercule.net/lastfm/lastfm_%{version}+dfsg.orig.tar.gz
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
# Fix some text/icon display issues with Qt >= 4.6
Patch14: qt46.diff
# Fix warnings when compiling with Qt >= 4.7
Patch15: qt47.diff
# Fix up icon installation path for Linux packages
Patch16: dirpaths.diff
Patch17: gcc41.diff
# loved radio is no longer supported, don't include it in the UI
Patch18: hide-loved-radio.diff
# don't scrobble tracks twice
Patch19: ipod-scrobble-fix.diff
# Explicitly select which browser to use. Set it in Tools | Options | Connection.
Patch52: browser-select.diff
#gw fix linking of the ipod plugin
Patch100: fix-linking.patch
#gw official patch to prevent a crash
Patch200: sidebar-crash-fix.diff
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
%setup -q -a 1 -n lastfm-%{version}
%autopatch -p1
#gw hack to remove patches for backports
%if %mdvver < 201100
%patch15 -p1 -R
%endif
%if %mdvver < 201010
%patch14 -p1 -R
%endif

bzcat %{SOURCE2} | tar -C bin/data/icons -xf - 

chmod -R +r .
perl -pi -e "s|\r\n|\n|" ChangeLog.txt

%build
%{qt4dir}/bin/qmake -config release
%make CXX="g++ -fPIC $(pkg-config --cflags libgpod-1.0)" libdir=%_libdir datadir=%_datadir

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
RUNDIR="%_libdir/%name"
export LD_LIBRARY_PATH="\${RUNDIR}\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
exec "\${RUNDIR}/last.fm" "$@"
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
Categories=Qt;AudioVideo;Audio;Player;X-MandrivaLinux-CrossDesktop;
EOF

mkdir -p %buildroot%_datadir/icons
cp -r icons/hicolor %buildroot%_datadir/icons/hicolor
find %buildroot -name .svn |xargs rm -rf

rm -f %buildroot%_libdir/%name/*.{lib,dylib}
#gw the dirpaths patch expects the data files there:
mv %buildroot%_libdir/%name/data %buildroot%_datadir/lastfm

#gw mac icons:
rm -f %buildroot%_datadir/%name/{icons/systray,about,install,wizard}_mac.png
#gw just for Windows:
rm -f %buildroot%_libdir/%name/LastFM.exe.config

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
%doc ChangeLog.txt README
%attr(755,root,root) %_bindir/%name
%_datadir/applications/mandriva-*
%_datadir/icons/hicolor/*/apps/lastfm*
%_libdir/%name
%_datadir/lastfm
%_datadir/services/lastfm.protocol
