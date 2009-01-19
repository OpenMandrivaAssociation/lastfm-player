%define name lastfm-player
%define oname player
%define version 1.5.1.31879
%define rel 3

Summary: Last.fm web radio player
Name: %{name}
Version: %{version}
Release: %mkrel %rel
Epoch: 1
Source0: http://cdn.last.fm/client/src/last.fm-%version.tar.bz2
Source1: lastfm-icons.tar.bz2
Source2: trayicons22.tar.bz2
# gw these patches come from the unofficial Debian package at:
# http://mehercule.net/staticpages/index.php/lastfm
Patch0: build-fixes.diff
Patch1: reduce-linkage.diff
Patch2: gcc-4.3.patch
Patch3: no-fingerprint-lib.diff
Patch4: alsa-uses-qdebug.diff
Patch5: check-soundcard-errors.diff
Patch6: tray-icon-size.diff
Patch7: hide-scrobbledir-option.diff
Patch8: hide-crashreport-option.diff
Patch9: tray-volume.diff
Patch10: set-locale.diff
Patch11: cheaper-save-geometry.diff
Patch12: set-firstrun-status.diff
Patch13: dirpaths.diff
Patch52: browser-select.diff

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
%setup -q -a 1 -n last.fm-%version
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch52 -p1

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
cp -r icons/crystalsvg %buildroot%_datadir/icons/hicolor
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
