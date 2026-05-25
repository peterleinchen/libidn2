Name:       libidn2
Version:    2.3.8
%define srcversion 2.3.8
Release:    1
Summary:    Implementation of IDNA2008 internationalized domain names
Group:      System/Libraries
License:    GPLv2+ or LGPLv3+
URL:        https://gitlab.com/libidn/libidn2
Packager: Peter Leinchen (for SFOS) <peterleinchen@t-online.de>

# Primary application source
Source0:   https://ftp.gnu.org/gnu/libidn/%{name}-%{srcversion}.tar.gz
Source1:   %{name}-%{version}.tar.gz

# Static-only dependencies inside the build workspace
Source2:    https://ftp.gnu.org/gnu/libunistring/libunistring-1.4.2.tar.gz
### Source2:    libunistring-1.4.2.tar.gz
## Source3:     https://ftp.gnu.org/gnu/libiconv/libiconv-1.19.tar.gz
### Source3:     libiconv-1.19.tar.gz

BuildRequires: gcc make

%description
Libidn2 is an implementation of the IDNA2008 specifications for
internationalized domain names. This package embeds its dependencies 
statically to simplify target compatibility on Sailfish OS ecosystems.

%package devel
Summary:    Development files for libidn2
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description devel
Header files and development files for compiling software against libidn2.

%package doc
Summary:    Documentation, man pages, and GTK-doc files for libidn2
Group:      Documentation
Requires:   %{name} = %{version}-%{release}

%description doc
Man pages, system info manuals, and HTML API reference documentation for libidn2.

%prep
# Extract primary source(s)
%setup -q -n %{name}-%{srcversion} -b 1

# Extract static packages into subdirectories for local compilation
mkdir -p deps/unistring deps/iconv
tar -xf %{SOURCE2} -C deps/unistring --strip-components=1
## tar -xf %{SOURCE3} -C deps/iconv --strip-components=1

%build
# Set absolute workspace pointer for temporary static targets
export BUILD_DIR_ROOT=$(pwd)/deps/inst

# MANDATORY FOR LEGACY TARGETS: Ensure the installation tree exists 
mkdir -p $BUILD_DIR_ROOT/lib $BUILD_DIR_ROOT/include

# 1. Compile Static libiconv using safe macro overrides
## cd deps/iconv
## %%configure \
##    --prefix=$BUILD_DIR_ROOT \
##    --libdir=$BUILD_DIR_ROOT/lib \
##    --enable-static \
##    --disable-shared \
##    --with-pic
## %%make_build
### Use make_install but isolate it to the temporary build folder
## %%make_install DESTDIR=""
## cd ../..

# 2. Compile Static libunistring using safe macro overrides
cd deps/unistring
./configure \
    --prefix=$BUILD_DIR_ROOT \
    --libdir=$BUILD_DIR_ROOT/lib \
    --enable-static \
    --disable-shared \
    --with-pic
    ## --with-libiconv-prefix=$BUILD_DIR_ROOT
%make_build
%make_install DESTDIR=""
cd ../..

# 3. Main libidn2 build using standard Sailfish target macros
# This automatically injects the correct CPU optimizations (-march, -mtune, etc.)
# Explicitly feed local paths directly into the configure stage variables
# Explicitly force the target variable to point directly to the static archive
gl_cv_lib_unistring=yes \
LIBS="$BUILD_DIR_ROOT/lib/libunistring.a" \
CFLAGS="%{optflags} -I$BUILD_DIR_ROOT/include" \
LDFLAGS="-L$BUILD_DIR_ROOT/lib" \
%configure \
    --disable-static \
    --enable-shared \
    --with-libunistring-prefix=$BUILD_DIR_ROOT
    ## --with-libiconv-prefix=$BUILD_DIR_ROOT

# Link static components cleanly into the final dynamic library
## %%make_build LDFLAGS="-L$BUILD_DIR_ROOT/lib -Wl,-Bstatic -lunistring -liconv -Wl,-Bdynamic"
## %%make_build LDFLAGS="-L$BUILD_DIR_ROOT/lib -Wl,-Bstatic -lunistring -Wl,-Bdynamic"
## above was working only for SFOS > 5.0, for legacy we need direct naming of libxxx.a with LIB=
%make_build

%install
rm -rf %{buildroot}
# Standard Sailfish install macro for the primary package
%make_install

# Automatically find and create a list of all localization files
%find_lang %{name}

# Clean up unwanted package tracking files
rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_infodir}/dir

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

## %%files
%files -f %{name}.lang
%doc AUTHORS NEWS README.md
%{_libdir}/libidn2.so.*
%{_bindir}/idn2

%files devel
%{_includedir}/idn2.h
%{_libdir}/libidn2.so
%{_libdir}/pkgconfig/libidn2.pc

%files doc
%defattr(-,root,root,-)
# Track the command-line application man page
%{_mandir}/man1/idn2.1*
# Track development function man pages
%{_mandir}/man3/*.3*
# Track the system info documentation page
%{_infodir}/libidn2.info*
# Explicitly track the unpackaged HTML API files:
%{_datadir}/gtk-doc/html/libidn2/