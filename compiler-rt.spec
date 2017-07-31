%{?scl:%scl_package compiler-rt}
%{!?scl:%global pkg_name %{name}}

%ifarch s390 s390x
# only limited set of libs available on s390(x) and the existing ones (stats, ubsan) don't provide debuginfo
%global debug_package
%endif

Name:		%{?scl_prefix}compiler-rt
Version:	4.0.1
Release:	1%{?dist}
Summary:	LLVM "compiler-rt" runtime libraries

License:	NCSA or MIT
URL:		http://llvm.org
Source0:	http://llvm.org/releases/%{version}/%{pkg_name}-%{version}.src.tar.xz

BuildRequires:	%{?scl_prefix}cmake
BuildRequires:	python
BuildRequires:  %{?scl_prefix}llvm-devel = %{version}
BuildRequires:  %{?scl_prefix}llvm-static = %{version}

%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%setup -q -n %{pkg_name}-%{version}.src

%build
mkdir -p _build
cd _build

# Use the scl-provided cmake instead of /usr/bin/cmake
%global __cmake %{_bindir}/cmake

%cmake .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_CONFIG_PATH:FILEPATH=%{_bindir}/llvm-config \
	\
%if 0%{?__isa_bits} == 64
        -DLLVM_LIBDIR_SUFFIX=64 \
%else
        -DLLVM_LIBDIR_SUFFIX= \
%endif
	-DCOMPILER_RT_INCLUDE_TESTS:BOOL=OFF # could be on?

make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}

# move sanitizer lists to better place
mkdir -p %{buildroot}%{_libdir}/clang/%{version}
for file in asan_blacklist.txt msan_blacklist.txt dfsan_blacklist.txt cfi_blacklist.txt dfsan_abilist.txt; do
	mv -v %{buildroot}%{_prefix}/${file} %{buildroot}%{_libdir}/clang/%{version}/ || :
done

# move sanitizer libs to better place
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib
mv -v %{buildroot}%{_prefix}/lib/linux/libclang_rt* %{buildroot}%{_libdir}/clang/%{version}/lib
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib/linux/
pushd %{buildroot}%{_libdir}/clang/%{version}/lib
for i in *.a *.syms *.so; do
	ln -s ../$i linux/$i
done

%check
cd _build
#make check-all

%files
%{_includedir}/*
%{_libdir}/clang/%{version}

%changelog
* Wed Jun 07 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-1
- 4.0.1 Release

* Wed Jun 07 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-3
- Build for llvm-toolset-7 rename

* Thu May 18 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-2
- Fix disabling debug on s390(x)

* Tue Mar 14 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-1
- compiler-rt 4.0.0 Final Release

* Thu Mar 02 2017 Dave Airlie <airlied@redhat.com> - 3.9.1-1
- compiler-rt 3.9.1

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 21 2016 Dan Horák <dan[at]danny.cz> - 3.9.0-3
- disable debuginfo on s390(x)

* Wed Nov 02 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-2
- build for new arches.

* Wed Oct 26 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-1
- compiler-rt 3.9.0 final release

* Mon May  2 2016 Tom Callaway <spot@fedoraproject.org> 3.8.0-2
- make symlinks to where the linker thinks these libs are

* Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
- compiler-rt 3.8.0 final release

* Thu Mar 03 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.2
- compiler-rt 3.8.0rc3

* Thu Feb 18 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.1
- compiler-rt 3.8.0rc2

* Fri Feb 05 2016 Dave Airlie <airlied@redhat.com> 3.7.1-3
- fix compiler-rt paths - from rwindz0@gmail.com - #1304605

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system
