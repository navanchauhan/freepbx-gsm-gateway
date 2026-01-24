/* include/asterisk/autoconfig.h.  Generated from autoconfig.h.in by configure.  */
/* include/asterisk/autoconfig.h.in.  Generated from configure.ac by autoheader.  */

#ifndef ASTERISK_AUTOCONFIG_H
#define ASTERISK_AUTOCONFIG_H
/* IWYU pragma: private, include "asterisk.h" */

#include "asterisk/buildopts.h" /* IWYU pragma: export */

/* Define to 'long' or 'long long' */
#define AST_JSON_INT_T long long

/* Define to 1 if internal poll should be used. */
/* #undef AST_POLL_COMPAT */

/* Define to enable XML documentation. */
#define AST_XML_DOCS 1

/* Define to 1 if your system's implementation of mutexes supports comparison
   of a mutex to its initializer. */
/* #undef CAN_COMPARE_MUTEX_TO_INIT_VALUE */

/* Define to 1 if the 'closedir' function returns void instead of int. */
/* #undef CLOSEDIR_VOID */

/* Some configure tests will unexpectedly fail if configure is run by a
   non-root user. These may be able to be tested at runtime. */
/* #undef CONFIGURE_RAN_AS_ROOT */

/* Define to 1 if using 'alloca.c'. */
/* #undef C_ALLOCA */

/* Define to 1 if anonymous semaphores work. */
#define HAS_WORKING_SEMAPHORE 1

/* Define to 1 if you have the 'acos' function. */
#define HAVE_ACOS 1

/* Define to 1 if you have the 'acosl' function. */
#define HAVE_ACOSL 1

/* Define to 1 if you have 'alloca', as a function or macro. */
#define HAVE_ALLOCA 1

/* Define to 1 if <alloca.h> works. */
#define HAVE_ALLOCA_H 1

/* Define to 1 if you have the <arpa/inet.h> header file. */
#define HAVE_ARPA_INET_H 1

/* Define to 1 if you have the <arpa/nameser.h> header file. */
#define HAVE_ARPA_NAMESER_H 1

/* Define to 1 if you have the 'asin' function. */
#define HAVE_ASIN 1

/* Define to 1 if you have the 'asinl' function. */
#define HAVE_ASINL 1

/* Define to 1 if you have the 'asprintf' function. */
#define HAVE_ASPRINTF 1

/* Define to 1 if you have the <assert.h> header file. */
#define HAVE_ASSERT_H 1

/* Define to 1 if you have the 'atan' function. */
#define HAVE_ATAN 1

/* Define to 1 if you have the 'atan2' function. */
#define HAVE_ATAN2 1

/* Define to 1 if you have the 'atan2l' function. */
#define HAVE_ATAN2L 1

/* Define to 1 if you have the 'atanl' function. */
#define HAVE_ATANL 1

/* Define to 1 if you have the 'atexit' function. */
#define HAVE_ATEXIT 1

/* Define to 1 if your GCC C compiler supports the 'always_inline' attribute.
   */
/* #undef HAVE_ATTRIBUTE_always_inline */

/* Define to 1 if your GCC C compiler supports the 'const' attribute. */
#define HAVE_ATTRIBUTE_const 1

/* Define to 1 if your GCC C compiler supports the 'constructor' attribute. */
#define HAVE_ATTRIBUTE_constructor 1

/* Define to 1 if your GCC C compiler supports the 'deprecated' attribute. */
#define HAVE_ATTRIBUTE_deprecated 1

/* Define to 1 if your GCC C compiler supports the 'destructor' attribute. */
#define HAVE_ATTRIBUTE_destructor 1

/* Define to 1 if your GCC C compiler supports the 'malloc' attribute. */
#define HAVE_ATTRIBUTE_malloc 1

/* Define to 1 if your GCC C compiler supports the 'may_alias' attribute. */
#define HAVE_ATTRIBUTE_may_alias 1

/* Define to 1 if your GCC C compiler supports the 'noreturn' attribute. */
#define HAVE_ATTRIBUTE_noreturn 1

/* Define to 1 if your GCC C compiler supports the 'pure' attribute. */
#define HAVE_ATTRIBUTE_pure 1

/* Define to 1 if your GCC C compiler supports the 'sentinel' attribute. */
#define HAVE_ATTRIBUTE_sentinel 1

/* Define to 1 if your GCC C compiler supports the 'unused' attribute. */
#define HAVE_ATTRIBUTE_unused 1

/* Define to 1 if your GCC C compiler supports the 'warn_unused_result'
   attribute. */
#define HAVE_ATTRIBUTE_warn_unused_result 1

/* Define to 1 if you have the Beanstalk Job Queue library. */
/* #undef HAVE_BEANSTALK */

/* Define to 1 if you have the Debug symbol decoding library. */
/* #undef HAVE_BFD */

/* Define to 1 if you have the Stack Backtrace library. */
#define HAVE_BKTR 1

/* Define to 1 if you have the Bluetooth library. */
/* #undef HAVE_BLUETOOTH */

/* Define to 1 if you have the file 'bridges/bridge_softmix/include/hrirs.h'.
   */
#define HAVE_BRIDGES_BRIDGE_SOFTMIX_INCLUDE_HRIRS_H 1

/* Define to 1 if byteswap.h macros are available. */
#define HAVE_BYTESWAP_H 1

/* Define to 1 if you have the POSIX 1.e capabilities library. */
/* #undef HAVE_CAP */

/* Define to 1 if you have the 'ceil' function. */
#define HAVE_CEIL 1

/* Define to 1 if you have the 'ceill' function. */
#define HAVE_CEILL 1

/* Define to 1 if your system has a working 'chown' function. */
#define HAVE_CHOWN 1

/* Define to 1 if you have the 'closefrom' function. */
#define HAVE_CLOSEFROM 1

/* Define to 1 if you have the Codec 2 Audio Decoder/Encoder library. */
/* #undef HAVE_CODEC2 */

/* Define to 1 if you have the Corosync library. */
/* #undef HAVE_COROSYNC */

/* Define to 1 if COROSYNC has the A callback only in corosync 1.x feature. */
/* #undef HAVE_COROSYNC_CFG_STATE_TRACK */

/* Define to 1 if you have the 'cos' function. */
#define HAVE_COS 1

/* Define to 1 if you have the 'cosl' function. */
#define HAVE_COSL 1

/* Define to 1 if you have the 'crypt' function. */
#define HAVE_CRYPT 1

/* Define to 1 if you have the OpenSSL Cryptography library. */
#define HAVE_CRYPTO 1

/* Define to 1 if you have the 'crypt_r' function. */
#define HAVE_CRYPT_R 1

/* Define to 1 if you have the <ctype.h> header file. */
#define HAVE_CTYPE_H 1

/* Define to 1 if you have a functional curl library. */
/* #undef HAVE_CURL */

/* define if the compiler supports basic C++11 syntax */
#define HAVE_CXX11 1

/* define if the compiler supports basic C++14 syntax */
#define HAVE_CXX14 1

/* define if the compiler supports basic C++17 syntax */
#define HAVE_CXX17 1

/* define if the compiler supports basic C++20 syntax */
#define HAVE_CXX20 1

/* define if the compiler supports basic C++23 syntax */
/* #undef HAVE_CXX23 */

/* Define to 1 if your C compiler provides __atomic operations. */
#define HAVE_C_ATOMICS 1

/* Define if your system has the DAHDI headers. */
/* #undef HAVE_DAHDI */

/* Define if your system has the DAHDI_ECHOCANCEL_FAX_MODE headers. */
/* #undef HAVE_DAHDI_ECHOCANCEL_FAX_MODE */

/* Define if your system has the DAHDI_HALF_FULL headers. */
/* #undef HAVE_DAHDI_HALF_FULL */

/* Define if your system has the DAHDI_LINEREVERSE_VMWI headers. */
/* #undef HAVE_DAHDI_LINEREVERSE_VMWI */

/* Define DAHDI headers version */
/* #undef HAVE_DAHDI_VERSION */

/* Define to 1 if you have the declaration of 'gethostbyname_r', and to 0 if
   you don't. */
#define HAVE_DECL_GETHOSTBYNAME_R 1

/* Define to 1 if you have the <dirent.h> header file, and it defines 'DIR'.
   */
#define HAVE_DIRENT_H 1

/* Define to 1 if your system has the dladdr() GNU extension */
#define HAVE_DLADDR 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you don't have 'vprintf' but do have '_doprnt.' */
/* #undef HAVE_DOPRNT */

/* Define to 1 if you have the 'dup2' function. */
#define HAVE_DUP2 1

/* Define to 1 if you have the 'eaccess' function. */
#define HAVE_EACCESS 1

/* Define to 1 if you have the 'endpwent' function. */
#define HAVE_ENDPWENT 1

/* Define to 1 if you have the <errno.h> header file. */
#define HAVE_ERRNO_H 1

/* Define to 1 if you have the 'euidaccess' function. */
#define HAVE_EUIDACCESS 1

/* Define to 1 if your system supports eventfd and the EFD_NONBLOCK and
   EFD_SEMAPHORE flags. */
#define HAVE_EVENTFD 1

/* Define to 1 if you have the 'exp' function. */
#define HAVE_EXP 1

/* Define to 1 if you have the 'exp10' function. */
#define HAVE_EXP10 1

/* Define to 1 if you have the 'exp10l' function. */
#define HAVE_EXP10L 1

/* Define to 1 if you have the 'exp2' function. */
#define HAVE_EXP2 1

/* Define to 1 if you have the 'exp2l' function. */
#define HAVE_EXP2L 1

/* Define to 1 if you have the 'expl' function. */
#define HAVE_EXPL 1

/* Define to 1 if you have the <fcntl.h> header file. */
#define HAVE_FCNTL_H 1

/* Define to 1 if you have the Ffmpeg and avcodec library. */
/* #undef HAVE_FFMPEG */

/* Define to 1 if you have the 'ffsll' function. */
#define HAVE_FFSLL 1

/* Define to 1 if you have the LIBFFTW3 library. */
/* #undef HAVE_FFTW3 */

/* Define to 1 if you have the <float.h> header file. */
#define HAVE_FLOAT_H 1

/* Define to 1 if you have the 'floor' function. */
#define HAVE_FLOOR 1

/* Define to 1 if you have the 'floorl' function. */
#define HAVE_FLOORL 1

/* Define to 1 if you have the 'fmod' function. */
#define HAVE_FMOD 1

/* Define to 1 if you have the 'fmodl' function. */
#define HAVE_FMODL 1

/* Define if your system has the FNM_CASEFOLD headers. */
#define HAVE_FNM_CASEFOLD 1

/* Define to 1 if you have the 'fork' function. */
#define HAVE_FORK 1

/* Define to 1 if you have the FreeTDS library. */
/* #undef HAVE_FREETDS */

/* Define to 1 if fseeko (and ftello) are declared in stdio.h. */
#define HAVE_FSEEKO 1

/* Define to 1 if you have the 'ftruncate' function. */
#define HAVE_FTRUNCATE 1

/* Define to 1 if your GCC C compiler provides __sync atomic operations. */
#define HAVE_GCC_ATOMICS 1

/* Define to 1 if you have the 'getcwd' function. */
#define HAVE_GETCWD 1

/* Define to 1 if you have the 'gethostbyname' function. */
#define HAVE_GETHOSTBYNAME 1

/* Define to 1 if your system has gethostbyname_r with 5 arguments. */
/* #undef HAVE_GETHOSTBYNAME_R_5 */

/* Define to 1 if your system has gethostbyname_r with 6 arguments. */
#define HAVE_GETHOSTBYNAME_R_6 1

/* Define to 1 if you have the 'gethostname' function. */
#define HAVE_GETHOSTNAME 1

/* Define if your system has the GETIFADDRS headers. */
#define HAVE_GETIFADDRS 1

/* Define to 1 if you have the 'getloadavg' function. */
#define HAVE_GETLOADAVG 1

/* Define to 1 if you have the 'getpagesize' function. */
#define HAVE_GETPAGESIZE 1

/* Define to 1 if you have the 'getpeereid' function. */
/* #undef HAVE_GETPEEREID */

/* Define to 1 if you have the 'gettimeofday' function. */
#define HAVE_GETTIMEOFDAY 1

/* Define to 1 if you have the 'glob' function. */
#define HAVE_GLOB 1

/* Define if your system has the GLOB_BRACE headers. */
#define HAVE_GLOB_BRACE 1

/* Define if your system has the GLOB_NOMAGIC headers. */
#define HAVE_GLOB_NOMAGIC 1

/* Define if your system has the GMIME libraries. */
/* #undef HAVE_GMIME */

/* Define to 1 if you have the <grp.h> header file. */
#define HAVE_GRP_H 1

/* Define to indicate the GSM library */
/* #undef HAVE_GSM */

/* Define to indicate that gsm.h is in gsm/gsm.h */
/* #undef HAVE_GSM_GSM_HEADER */

/* Define to indicate that gsm.h has no prefix for its location */
#define HAVE_GSM_HEADER 1

/* Define if your system has the GTK2 libraries. */
/* #undef HAVE_GTK2 */

/* Define to 1 if you have the Hoard Memory Allocator library. */
/* #undef HAVE_HOARD */

/* Define to 1 if arpa/inet.h includes a htonll definition. */
/* #undef HAVE_HTONLL */

/* Define to 1 if you have the iCal library. */
/* #undef HAVE_ICAL */

/* Define to 1 if you have the Iconv library. */
#define HAVE_ICONV 1

/* Define to 1 if you have the Iksemel Jabber library. */
/* #undef HAVE_IKSEMEL */

/* Define if your system has the ILBC libraries. */
/* #undef HAVE_ILBC */

/* Define if your system has the UW IMAP Toolkit c-client library. */
/* #undef HAVE_IMAP_TK */

/* Define if your system has the UW IMAP Toolkit c-client library version 2006
   or greater. */
/* #undef HAVE_IMAP_TK2006 */

/* Define to 1 if you have the 'inet_aton' function. */
#define HAVE_INET_ATON 1

/* Define to 1 if you have the 'inet_ntoa' function. */
#define HAVE_INET_NTOA 1

/* Define to 1 if you have the inotify support library. */
#define HAVE_INOTIFY 1

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the iODBC library. */
/* #undef HAVE_IODBC */

/* Define to 1 if you have the 'ioperm' function. */
#define HAVE_IOPERM 1

/* Define if your system has the IP_MTU_DISCOVER headers. */
#define HAVE_IP_MTU_DISCOVER 1

/* Define to 1 if you have the 'isascii' function. */
#define HAVE_ISASCII 1

/* Define to 1 if you have the Jack Audio Connection Kit library. */
/* #undef HAVE_JACK */

/* Define if your system has the JANSSON libraries. */
/* #undef HAVE_JANSSON */

/* Define if your system has JANSSON_BUNDLED */
#define HAVE_JANSSON_BUNDLED 1

/* Define to 1 if you have the 'kevent64' function. */
/* #undef HAVE_KEVENT64 */

/* Define to 1 if you have the kqueue support library. */
/* #undef HAVE_KQUEUE */

/* Define to 1 if you have the OpenLDAP library. */
/* #undef HAVE_LDAP */

/* Define if your system has the LIBEDIT libraries. */
#define HAVE_LIBEDIT 1

/* Define if your system has the LIBEDIT_IS_UNICODE headers. */
#define HAVE_LIBEDIT_IS_UNICODE 1

/* Define to 1 if you have the <libintl.h> header file. */
#define HAVE_LIBINTL_H 1

/* Define if your system has the LIBJWT libraries. */
/* #undef HAVE_LIBJWT */

/* Define if your system has LIBJWT_BUNDLED */
/* #undef HAVE_LIBJWT_BUNDLED */

/* Define to 1 if you have the 'm' library (-lm). */
#define HAVE_LIBM 1

/* Define if your system has the LIBXML2 libraries. */
#define HAVE_LIBXML2 1

/* Define to 1 if you have the LibXSLT library. */
/* #undef HAVE_LIBXSLT */

/* Define to 1 if LIBXSLT has the LibXSLT Library Cleanup Function feature. */
/* #undef HAVE_LIBXSLT_CLEANUP */

/* Define to 1 if you have the <limits.h> header file. */
#define HAVE_LIMITS_H 1

/* Define to 1 if your system has linux/compiler.h. */
/* #undef HAVE_LINUX_COMPILER_H */

/* Define to 1 if limits.h includes a LLONG_MAX definition. */
#define HAVE_LLONG_MAX 1

/* Define to 1 if you have the <locale.h> header file. */
#define HAVE_LOCALE_H 1

/* Define to 1 if your system defines the locale_t type in locale.h */
#define HAVE_LOCALE_T_IN_LOCALE_H 1

/* Define to 1 if your system defines the locale_t type in xlocale.h */
/* #undef HAVE_LOCALE_T_IN_XLOCALE_H */

/* Define to 1 if you have the 'log' function. */
#define HAVE_LOG 1

/* Define to 1 if you have the 'log10' function. */
#define HAVE_LOG10 1

/* Define to 1 if you have the 'log10l' function. */
#define HAVE_LOG10L 1

/* Define to 1 if you have the 'log2' function. */
#define HAVE_LOG2 1

/* Define to 1 if you have the 'log2l' function. */
#define HAVE_LOG2L 1

/* Define to 1 if you have the 'logl' function. */
#define HAVE_LOGL 1

/* Define to 1 if the type 'long double' works and has more range or precision
   than 'double'. */
#define HAVE_LONG_DOUBLE_WIDER 1

/* Define to 1 if you have the Lua library. */
/* #undef HAVE_LUA */

/* Define to 1 if you have the <malloc.h> header file. */
#define HAVE_MALLOC_H 1

/* Define to 1 if you have the 'malloc_trim' function. */
#define HAVE_MALLOC_TRIM 1

/* Define to 1 if you have the <math.h> header file. */
#define HAVE_MATH_H 1

/* Define to 1 if you have the 'memchr' function. */
#define HAVE_MEMCHR 1

/* Define to 1 if you have the 'memmove' function. */
#define HAVE_MEMMOVE 1

/* Define to 1 if you have the 'memset' function. */
#define HAVE_MEMSET 1

/* Define to 1 if you have the <minix/config.h> header file. */
/* #undef HAVE_MINIX_CONFIG_H */

/* Define to 1 if you have the 'mkdir' function. */
#define HAVE_MKDIR 1

/* Define to 1 if you have the 'mkdtemp' function. */
#define HAVE_MKDTEMP 1

/* Define to 1 if you have a working 'mmap' system call. */
#define HAVE_MMAP 1

/* Define to 1 if you have the 'munmap' function. */
#define HAVE_MUNMAP 1

/* Define if your system has the MYSQLCLIENT libraries. */
/* #undef HAVE_MYSQLCLIENT */

/* Define to 1 if mysql/mysql.h has bool defined. */
/* #undef HAVE_MYSQLCLIENT_BOOL */

/* Define to 1 if mysql/mysql.h has my_bool defined. */
/* #undef HAVE_MYSQLCLIENT_MY_BOOL */

/* Define to 1 if you have the <ndir.h> header file, and it defines 'DIR'. */
/* #undef HAVE_NDIR_H */

/* Define if your system has the NEON libraries. */
/* #undef HAVE_NEON */

/* Define if your system has the NEON29 libraries. */
/* #undef HAVE_NEON29 */

/* Define to 1 if you have the <netdb.h> header file. */
#define HAVE_NETDB_H 1

/* Define to 1 if you have the <netinet/in.h> header file. */
#define HAVE_NETINET_IN_H 1

/* Define if your system has the NETSNMP libraries. */
/* #undef HAVE_NETSNMP */

/* Define to 1 if you have the 'newlocale' function. */
#define HAVE_NEWLOCALE 1

/* Define to 1 if you have the newt library. */
/* #undef HAVE_NEWT */

/* Define to 1 if arpa/inet.h includes a ntohll definition. */
/* #undef HAVE_NTOHLL */

/* Define to 1 if your C library can safely print NULL to string formats. */
#define HAVE_NULLSAFE_PRINTF 1

/* Define to 1 if your ODBC library has wide (Unicode) types. */
/* #undef HAVE_ODBC_WCHAR */

/* Define to 1 if you have the OGG library. */
/* #undef HAVE_OGG */

/* Define to 1 if you have the MFR2 library. */
/* #undef HAVE_OPENR2 */

/* Define if your system has the OPENSSL libraries. */
#define HAVE_OPENSSL 1

/* Define to 1 if CRYPTO has the OpenSSL BIO Method Support feature. */
#define HAVE_OPENSSL_BIO_METHOD 1

/* Define to 1 if you have the Opus library. */
/* #undef HAVE_OPUS */

/* Define to 1 if you have the Opusfile library. */
/* #undef HAVE_OPUSFILE */

/* Define to 1 if your system defines the file flag O_EVTONLY in fcntl.h */
/* #undef HAVE_O_EVTONLY */

/* Define to 1 if your system defines the file flag O_SYMLINK in fcntl.h */
/* #undef HAVE_O_SYMLINK */

/* Define to support libc with permanent dlopen. */
/* #undef HAVE_PERMANENT_DLOPEN */

/* Define to indicate the PostgreSQL library */
/* #undef HAVE_PGSQL */

/* Define to indicate presence of the pg_encoding_to_char API. */
/* #undef HAVE_PGSQL_pg_encoding_to_char */

/* Define to 1 if you have the 'pipe2' function. */
#define HAVE_PIPE2 1

/* Define if your system has the PJPROJECT libraries. */
#define HAVE_PJPROJECT 1

/* Define if your system has PJPROJECT_BUNDLED */
#define HAVE_PJPROJECT_BUNDLED 1

/* Define if doing a bundled pjproject out-of-tree build. */
/* #undef HAVE_PJPROJECT_BUNDLED_OOT */

/* Define to 1 if on_valid_pair callback is present. */
#define HAVE_PJPROJECT_ON_VALID_ICE_PAIR_CALLBACK 1

/* Define to 1 if PJPROJECT has the pjsip_auth_clt_deinit support feature. */
#define HAVE_PJSIP_AUTH_CLT_DEINIT 1

/* Define to 1 if PJPROJECT has the PJSIP Auth new digests like SHA-256 and
   SHA-512-256 feature. */
#define HAVE_PJSIP_AUTH_NEW_DIGESTS 1

/* Define to 1 if PJPROJECT has the PJSIP Dialog Create UAS with Incremented
   Lock feature. */
#define HAVE_PJSIP_DLG_CREATE_UAS_AND_INC_LOCK 1

/* Define if your system has the PJSIP_ENDPOINT_COMPACT_FORM headers. */
#define HAVE_PJSIP_ENDPOINT_COMPACT_FORM 1

/* Define to 1 if PJPROJECT has the PJSIP EVSUB Group Lock support feature. */
#define HAVE_PJSIP_EVSUB_GRP_LOCK 1

/* Define to 1 if PJPROJECT has the PJSIP External Resolver Support feature.
   */
#define HAVE_PJSIP_EXTERNAL_RESOLVER 1

/* Define to 1 if PJPROJECT has the pjsip_get_dest_info support feature. */
#define HAVE_PJSIP_GET_DEST_INFO 1

/* Define if your system has the PJSIP_INV_ACCEPT_MULTIPLE_SDP_ANSWERS
   headers. */
#define HAVE_PJSIP_INV_ACCEPT_MULTIPLE_SDP_ANSWERS 1

/* Define to 1 if PJPROJECT has the PJSIP INVITE Session Reference Count
   support feature. */
#define HAVE_PJSIP_INV_SESSION_REF 1

/* Define if your system has the PJSIP_OAUTH_AUTHENTICATION headers. */
#define HAVE_PJSIP_OAUTH_AUTHENTICATION 1

/* Define if your system has the PJSIP_REPLACE_MEDIA_STREAM headers. */
#define HAVE_PJSIP_REPLACE_MEDIA_STREAM 1

/* Define if your system has the PJSIP_TLS_1_1 headers. */
#define HAVE_PJSIP_TLS_1_1 1

/* Define if your system has the PJSIP_TLS_1_2 headers. */
#define HAVE_PJSIP_TLS_1_2 1

/* Define if your system has the PJSIP_TLS_1_3 headers. */
#define HAVE_PJSIP_TLS_1_3 1

/* Define if your system has the PJSIP_TLS_TRANSPORT_PROTO headers. */
#define HAVE_PJSIP_TLS_TRANSPORT_PROTO 1

/* Define to 1 if PJPROJECT has the PJSIP TLS Transport Restart Support
   feature. */
#define HAVE_PJSIP_TLS_TRANSPORT_RESTART 1

/* Define if your system has the PJSIP_TRANSPORT_DISABLE_CONNECTION_REUSE
   headers. */
#define HAVE_PJSIP_TRANSPORT_DISABLE_CONNECTION_REUSE 1

/* Define to 1 if PJPROJECT has the pjsip_tsx_layer_find_tsx2 support feature.
   */
#define HAVE_PJSIP_TSX_LAYER_FIND_TSX2 1

/* Define to 1 if PJPROJECT has the pj_ssl_cert_load_from_files2 support
   feature. */
#define HAVE_PJ_SSL_CERT_LOAD_FROM_FILES2 1

/* Define to 1 if PJPROJECT has the PJSIP Transaction Group Lock Support
   feature. */
#define HAVE_PJ_TRANSACTION_GRP_LOCK 1

/* Define to 1 if your system defines IP_PKTINFO. */
#define HAVE_PKTINFO 1

/* Define to 1 if you have the popt library. */
/* #undef HAVE_POPT */

/* Define if your system has the PORTAUDIO libraries. */
/* #undef HAVE_PORTAUDIO */

/* Define to 1 if you have the 'pow' function. */
#define HAVE_POW 1

/* Define to 1 if you have the 'powl' function. */
#define HAVE_POWL 1

/* Define to 1 if you have the 'ppoll' function. */
#define HAVE_PPOLL 1

/* Define to 1 if you have the ISDN PRI library. */
/* #undef HAVE_PRI */

/* Define to 1 if PRI has the ISDN PRI advice of charge supplementary service
   events feature. */
/* #undef HAVE_PRI_AOC_EVENTS */

/* Define to 1 if PRI has the ISDN PRI call hold feature. */
/* #undef HAVE_PRI_CALL_HOLD */

/* Define to 1 if PRI has the ISDN PRI call rerouting and call deflection
   feature. */
/* #undef HAVE_PRI_CALL_REROUTING */

/* Define to 1 if PRI has the ISDN PRI call waiting supplementary service
   feature. */
/* #undef HAVE_PRI_CALL_WAITING */

/* Define to 1 if PRI has the ISDN PRI call completion supplementary service
   feature. */
/* #undef HAVE_PRI_CCSS */

/* Define to 1 if PRI has the ISDN PRI Date/time ie send policy feature. */
/* #undef HAVE_PRI_DATETIME_SEND */

/* Define to 1 if PRI has the ISDN PRI user display text IE contents during
   call feature. */
/* #undef HAVE_PRI_DISPLAY_TEXT */

/* Define to 1 if PRI has the ISDN PRI hangup fix feature. */
/* #undef HAVE_PRI_HANGUP_FIX */

/* Define to 1 if PRI has the ISDN PRI set_inbanddisconnect feature. */
/* #undef HAVE_PRI_INBANDDISCONNECT */

/* Define to 1 if PRI has the ISDN Layer 2 persistence option feature. */
/* #undef HAVE_PRI_L2_PERSISTENCE */

/* Define to 1 if PRI has the ISDN PRI Malicious Call ID feature. */
/* #undef HAVE_PRI_MCID */

/* Define to 1 if PRI has the ISDN PRI Message Waiting Indication feature. */
/* #undef HAVE_PRI_MWI */

/* Define to 1 if PRI has the ISDN PRI Message Waiting Indication (Fixed)
   feature. */
/* #undef HAVE_PRI_MWI_V2 */

/* Define to 1 if PRI has the ISDN progress with cause feature. */
/* #undef HAVE_PRI_PROG_W_CAUSE */

/* Define to 1 if PRI has the ISDN reverse charge feature. */
/* #undef HAVE_PRI_REVERSE_CHARGE */

/* Define to 1 if PRI has the ISDN service messages feature. */
/* #undef HAVE_PRI_SERVICE_MESSAGES */

/* Define to 1 if PRI has the ISDN PRI progress inband ie in SETUP ACK
   feature. */
/* #undef HAVE_PRI_SETUP_ACK_INBAND */

/* Define to 1 if PRI has the ISDN PRI keypad facility in SETUP feature. */
/* #undef HAVE_PRI_SETUP_KEYPAD */

/* Define to 1 if PRI has the ISDN PRI subaddressing feature. */
/* #undef HAVE_PRI_SUBADDR */

/* Define to 1 if PRI has the ISDN PRI call transfer supplementary service
   feature. */
/* #undef HAVE_PRI_TRANSFER */

/* Define if you have POSIX threads libraries and header files. */
#define HAVE_PTHREAD 1

/* Define to 1 if your system defines PTHREAD_MUTEX_ADAPTIVE_NP in pthread.h
   */
#define HAVE_PTHREAD_MUTEX_ADAPTIVE_NP 1

/* Define to 1 if your system defines PTHREAD_MUTEX_RECURSIVE_NP in pthread.h
   */
#define HAVE_PTHREAD_MUTEX_RECURSIVE_NP 1

/* Have PTHREAD_PRIO_INHERIT. */
#define HAVE_PTHREAD_PRIO_INHERIT 1

/* Define if your system has the PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP
   headers. */
#define HAVE_PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP 1

/* Define if your system has the PTHREAD_RWLOCK_INITIALIZER headers. */
#define HAVE_PTHREAD_RWLOCK_INITIALIZER 1

/* Define to 1 if your system defines PTHREAD_RWLOCK_PREFER_WRITER_NP in
   pthread.h */
#define HAVE_PTHREAD_RWLOCK_PREFER_WRITER_NP 1

/* Define if your system has pthread_rwlock_timedwrlock() */
#define HAVE_PTHREAD_RWLOCK_TIMEDWRLOCK 1

/* Define to 1 if your system has pthread_spinlock_t in pthread.h */
#define HAVE_PTHREAD_SPINLOCK 1

/* Define to 1 if the system has the type 'ptrdiff_t'. */
#define HAVE_PTRDIFF_T 1

/* Define to 1 if you have the 'putenv' function. */
#define HAVE_PUTENV 1

/* Define to 1 if you have the <pwd.h> header file. */
#define HAVE_PWD_H 1

/* Define if your system has the PYTHONDEV libraries. */
/* #undef HAVE_PYTHONDEV */

/* Define to 1 if you have the Radius Client library. */
/* #undef HAVE_RADIUS */

/* Define to 1 if you have the 'regcomp' function. */
#define HAVE_REGCOMP 1

/* Define to 1 if you have the <regex.h> header file. */
#define HAVE_REGEX_H 1

/* Define to 1 if you have the 'remainder' function. */
#define HAVE_REMAINDER 1

/* Define to 1 if you have the 'remainderl' function. */
#define HAVE_REMAINDERL 1

/* Define to 1 if you have the LIBRESAMPLE library. */
/* #undef HAVE_RESAMPLE */

/* Define to 1 if you have the <resolv.h> header file. */
#define HAVE_RESOLV_H 1

/* Define to 1 if your system has the close resolver function. */
/* #undef HAVE_RES_CLOSE */

/* Define to 1 if your system has the ndestroy resolver function. */
/* #undef HAVE_RES_NDESTROY */

/* Define to 1 if your system has the re-entrant resolver functions. */
#define HAVE_RES_NINIT 1

/* Define to 1 if you have the 're_comp' function. */
#define HAVE_RE_COMP 1

/* Define to 1 if you have the 'rint' function. */
#define HAVE_RINT 1

/* Define to 1 if you have the 'rintl' function. */
#define HAVE_RINTL 1

/* Define to 1 if you have the 'round' function. */
#define HAVE_ROUND 1

/* Define to 1 if you have the 'roundf' function. */
#define HAVE_ROUNDF 1

/* Define to 1 if you have the 'roundl' function. */
#define HAVE_ROUNDL 1

/* Define to 1 if rt has the Realtime functions feature. */
#define HAVE_RT 1

/* Define if your system has the RTLD_NOLOAD headers. */
#define HAVE_RTLD_NOLOAD 1

/* Define to 1 if your system has /sbin/launchd. */
/* #undef HAVE_SBIN_LAUNCHD */

/* Define to 1 if you have the <sched.h> header file. */
#define HAVE_SCHED_H 1

/* Define if your system has the SDL libraries. */
/* #undef HAVE_SDL */

/* Define to 1 if you have the Sdl Image library. */
/* #undef HAVE_SDL_IMAGE */

/* Define to 1 if you have the 'select' function. */
#define HAVE_SELECT 1

/* Define to 1 if you have the 'setenv' function. */
#define HAVE_SETENV 1

/* Define to 1 if you have the 'sin' function. */
#define HAVE_SIN 1

/* Define to 1 if you have the 'sinl' function. */
#define HAVE_SINL 1

/* Define to 1 if you have the libsndfile library. */
/* #undef HAVE_SNDFILE */

/* Define to 1 if you have the 'socket' function. */
#define HAVE_SOCKET 1

/* Define to 1 if your socket() implementation has the IPV6_V6ONLY socket
   option. */
#define HAVE_SOCK_IPV6_V6ONLY 1

/* Define to 1 if your socket() implementation can accept SOCK_NONBLOCK. */
#define HAVE_SOCK_NONBLOCK 1

/* Define to 1 if your system has soxmix application. */
/* #undef HAVE_SOXMIX */

/* Define if your system has the SPANDSP headers. */
/* #undef HAVE_SPANDSP */

/* Define to 1 if you have the Speex library. */
/* #undef HAVE_SPEEX */

/* Define to 1 if you have the SpeexDSP library. */
/* #undef HAVE_SPEEXDSP */

/* Define to 1 if you have the speex_preprocess_ctl library. */
/* #undef HAVE_SPEEX_PREPROCESS */

/* Define to 1 if you have the SQLite library. */
#define HAVE_SQLITE3 1

/* Define to 1 if you have the 'sqrtl' function. */
#define HAVE_SQRTL 1

/* Define to 1 if you have the Secure RTP library. */
/* #undef HAVE_SRTP */

/* Define to 1 if SRTP has the SRTP Library AES-192 (ICM) feature. */
/* #undef HAVE_SRTP_192 */

/* Define to 1 if SRTP has the SRTP Library AES-256 (ICM) feature. */
/* #undef HAVE_SRTP_256 */

/* Define to 1 if SRTP has the SRTP Library AES-128 (GCM) and AES-256 (GCM)
   feature. */
/* #undef HAVE_SRTP_GCM */

/* Define to 1 if SRTP has the SRTP Library Version Function feature. */
/* #undef HAVE_SRTP_GET_VERSION */

/* Define to 1 if SRTP has the SRTP Library Shutdown Function feature. */
/* #undef HAVE_SRTP_SHUTDOWN */

/* Define to the version of the srtp library. */
/* #undef HAVE_SRTP_VERSION */

/* Define to 1 if you have the ISDN SS7 library. */
/* #undef HAVE_SS7 */

/* Define to 1 if 'stat' has the bug that it succeeds when given the
   zero-length file name argument. */
/* #undef HAVE_STAT_EMPTY_STRING_BUG */

/* Define to 1 if you have the <stdarg.h> header file. */
#define HAVE_STDARG_H 1

/* Define to 1 if stdbool.h conforms to C99. */
#define HAVE_STDBOOL_H 1

/* Define to 1 if you have the <stddef.h> header file. */
#define HAVE_STDDEF_H 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdio.h> header file. */
#define HAVE_STDIO_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the 'strcasecmp' function. */
#define HAVE_STRCASECMP 1

/* Define to 1 if you have the 'strcasestr' function. */
#define HAVE_STRCASESTR 1

/* Define to 1 if you have the 'strchr' function. */
#define HAVE_STRCHR 1

/* Define to 1 if you have the 'strcoll' function and it is properly defined.
   */
#define HAVE_STRCOLL 1

/* Define to 1 if you have the 'strcspn' function. */
#define HAVE_STRCSPN 1

/* Define to 1 if you have the 'strdup' function. */
#define HAVE_STRDUP 1

/* Define to 1 if you have the 'strerror' function. */
#define HAVE_STRERROR 1

/* Define to 1 if you have the 'strftime' function. */
#define HAVE_STRFTIME 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the 'strlcat' function. */
/* #undef HAVE_STRLCAT */

/* Define to 1 if you have the 'strlcpy' function. */
/* #undef HAVE_STRLCPY */

/* Define to 1 if you have the 'strncasecmp' function. */
#define HAVE_STRNCASECMP 1

/* Define to 1 if you have the 'strndup' function. */
#define HAVE_STRNDUP 1

/* Define to 1 if you have the 'strnlen' function. */
#define HAVE_STRNLEN 1

/* Define to 1 if you have the 'strrchr' function. */
#define HAVE_STRRCHR 1

/* Define to 1 if you have the 'strsep' function. */
#define HAVE_STRSEP 1

/* Define to 1 if you have the 'strspn' function. */
#define HAVE_STRSPN 1

/* Define to 1 if you have the 'strstr' function. */
#define HAVE_STRSTR 1

/* Define to 1 if you have the 'strtod' function. */
#define HAVE_STRTOD 1

/* Define to 1 if you have the 'strtol' function. */
#define HAVE_STRTOL 1

/* Define to 1 if you have the 'strtold' function. */
#define HAVE_STRTOLD 1

/* Define to 1 if you have the 'strtoq' function. */
#define HAVE_STRTOQ 1

/* Define to 1 if 'ifr_ifru.ifru_hwaddr' is a member of 'struct ifreq'. */
#define HAVE_STRUCT_IFREQ_IFR_IFRU_IFRU_HWADDR 1

/* Define to 1 if 'sin6_len' is a member of 'struct sockaddr_in6'. */
/* #undef HAVE_STRUCT_SOCKADDR_IN6_SIN6_LEN */

/* Define to 1 if 'sin_len' is a member of 'struct sockaddr_in'. */
/* #undef HAVE_STRUCT_SOCKADDR_IN_SIN_LEN */

/* Define to 1 if 'uid' is a member of 'struct sockpeercred'. */
/* #undef HAVE_STRUCT_SOCKPEERCRED_UID */

/* Define to 1 if 'st_blksize' is a member of 'struct stat'. */
#define HAVE_STRUCT_STAT_ST_BLKSIZE 1

/* Define to 1 if 'st_mtim' is a member of 'struct stat'. */
#define HAVE_STRUCT_STAT_ST_MTIM 1

/* Define to 1 if 'st_mtimensec' is a member of 'struct stat'. */
/* #undef HAVE_STRUCT_STAT_ST_MTIMENSEC */

/* Define to 1 if 'st_mtimespec' is a member of 'struct stat'. */
/* #undef HAVE_STRUCT_STAT_ST_MTIMESPEC */

/* Define to 1 if 'cr_uid' is a member of 'struct ucred'. */
/* #undef HAVE_STRUCT_UCRED_CR_UID */

/* Define to 1 if 'uid' is a member of 'struct ucred'. */
#define HAVE_STRUCT_UCRED_UID 1

/* Define to 1 if '_u._ext.nsaddrs' is a member of 'struct __res_state'. */
#define HAVE_STRUCT___RES_STATE__U__EXT_NSADDRS 1

/* Define to 1 if you have the 'swapctl' function. */
/* #undef HAVE_SWAPCTL */

/* Define to 1 if you have the 'sysctl' function. */
/* #undef HAVE_SYSCTL */

/* Define to 1 if your system has sysinfo support */
#define HAVE_SYSINFO 1

/* Define if your system has the SYSLOG_FACILITY_LOG_AUTH headers. */
#define HAVE_SYSLOG_FACILITY_LOG_AUTH 1

/* Define if your system has the SYSLOG_FACILITY_LOG_AUTHPRIV headers. */
#define HAVE_SYSLOG_FACILITY_LOG_AUTHPRIV 1

/* Define if your system has the SYSLOG_FACILITY_LOG_CRON headers. */
#define HAVE_SYSLOG_FACILITY_LOG_CRON 1

/* Define if your system has the SYSLOG_FACILITY_LOG_DAEMON headers. */
#define HAVE_SYSLOG_FACILITY_LOG_DAEMON 1

/* Define if your system has the SYSLOG_FACILITY_LOG_FTP headers. */
#define HAVE_SYSLOG_FACILITY_LOG_FTP 1

/* Define if your system has the SYSLOG_FACILITY_LOG_KERN headers. */
#define HAVE_SYSLOG_FACILITY_LOG_KERN 1

/* Define if your system has the SYSLOG_FACILITY_LOG_LPR headers. */
#define HAVE_SYSLOG_FACILITY_LOG_LPR 1

/* Define if your system has the SYSLOG_FACILITY_LOG_MAIL headers. */
#define HAVE_SYSLOG_FACILITY_LOG_MAIL 1

/* Define if your system has the SYSLOG_FACILITY_LOG_NEWS headers. */
#define HAVE_SYSLOG_FACILITY_LOG_NEWS 1

/* Define if your system has the SYSLOG_FACILITY_LOG_SYSLOG headers. */
#define HAVE_SYSLOG_FACILITY_LOG_SYSLOG 1

/* Define if your system has the SYSLOG_FACILITY_LOG_UUCP headers. */
#define HAVE_SYSLOG_FACILITY_LOG_UUCP 1

/* Define to 1 if you have the <syslog.h> header file. */
#define HAVE_SYSLOG_H 1

/* Define if your system has the SYSTEMD libraries. */
/* #undef HAVE_SYSTEMD */

/* Define to 1 if you have the <sys/dir.h> header file, and it defines 'DIR'.
   */
/* #undef HAVE_SYS_DIR_H */

/* Define to 1 if your sys/endian.h header file provides the bswap16 macro. */
/* #undef HAVE_SYS_ENDIAN_BSWAP16 */

/* Define to 1 if your sys/endian.h header file provides the __swap16 macro.
   */
/* #undef HAVE_SYS_ENDIAN_SWAP16 */

/* Define to 1 if you have the <sys/event.h> header file. */
/* #undef HAVE_SYS_EVENT_H */

/* Define to 1 if you have the <sys/file.h> header file. */
#define HAVE_SYS_FILE_H 1

/* Define to 1 if you have the <sys/ioctl.h> header file. */
#define HAVE_SYS_IOCTL_H 1

/* Define to 1 if you have the <sys/ndir.h> header file, and it defines 'DIR'.
   */
/* #undef HAVE_SYS_NDIR_H */

/* Define to 1 if you have the <sys/param.h> header file. */
#define HAVE_SYS_PARAM_H 1

/* Define to 1 if your system has working sys/poll.h */
#define HAVE_SYS_POLL_H 1

/* Define to 1 if you have the <sys/resource.h> header file. */
#define HAVE_SYS_RESOURCE_H 1

/* Define to 1 if you have the <sys/select.h> header file. */
#define HAVE_SYS_SELECT_H 1

/* Define to 1 if you have the <sys/socket.h> header file. */
#define HAVE_SYS_SOCKET_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/time.h> header file. */
#define HAVE_SYS_TIME_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <sys/un.h> header file. */
#define HAVE_SYS_UN_H 1

/* Define to 1 if you have <sys/wait.h> that is POSIX.1 compatible. */
#define HAVE_SYS_WAIT_H 1

/* Define to 1 if you have the 'tan' function. */
#define HAVE_TAN 1

/* Define to 1 if you have the 'tanl' function. */
#define HAVE_TANL 1

/* Define to 1 if you have the <termios.h> header file. */
#define HAVE_TERMIOS_H 1

/* Define if your system has the TIMERFD headers. */
#define HAVE_TIMERFD 1

/* Define to 1 if your system defines timersub. */
#define HAVE_TIMERSUB 1

/* Define to 1 if you have the <time.h> header file. */
#define HAVE_TIME_H 1

/* Define to 1 if you have the tonezone library. */
/* #undef HAVE_TONEZONE */

/* Define to 1 if you have the 'trunc' function. */
#define HAVE_TRUNC 1

/* Define to 1 if you have the 'truncl' function. */
#define HAVE_TRUNCL 1

/* Define to 1 if you have the unbound library. */
/* #undef HAVE_UNBOUND */

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Define to 1 if you have the unixODBC library. */
/* #undef HAVE_UNIXODBC */

/* Define to 1 if you have the 'unsetenv' function. */
#define HAVE_UNSETENV 1

/* Define to 1 if you have the uriparser library library. */
/* #undef HAVE_URIPARSER */

/* Define to 1 if you have the 'uselocale' function. */
#define HAVE_USELOCALE 1

/* Define to 1 if you have the 'utime' function. */
#define HAVE_UTIME 1

/* Define to 1 if you have the <utime.h> header file. */
#define HAVE_UTIME_H 1

/* Define to 1 if 'utime(file, NULL)' sets file's timestamp to the present. */
#define HAVE_UTIME_NULL 1

/* Define to 1 if you have the 'uuid_generate_random' function. */
/* #undef HAVE_UUID_GENERATE_RANDOM */

/* Define to 1 if your system can support larger than default select bitmasks.
   */
/* #undef HAVE_VARIABLE_FDSET */

/* Define to 1 if you have the 'vasprintf' function. */
#define HAVE_VASPRINTF 1

/* Define to 1 if you have the 'vfork' function. */
#define HAVE_VFORK 1

/* Define to 1 if you have the <vfork.h> header file. */
/* #undef HAVE_VFORK_H */

/* Define to 1 if your system has linux/videodev.h. */
/* #undef HAVE_VIDEODEV_H */

/* Define to 1 if you have the Vorbis library. */
/* #undef HAVE_VORBIS */

/* Define if your system has OV_CALLBACKS_NOCLOSE declared. */
/* #undef HAVE_VORBIS_OPEN_CALLBACKS */

/* Define to 1 if you have the 'vprintf' function. */
#define HAVE_VPRINTF 1

/* Define to 1 if you have the <wchar.h> header file. */
#define HAVE_WCHAR_H 1

/* Define to 1 if you have the <winsock2.h> header file. */
/* #undef HAVE_WINSOCK2_H */

/* Define to 1 if you have the <winsock.h> header file. */
/* #undef HAVE_WINSOCK_H */

/* Define to 1 if `fork' works. */
#define HAVE_WORKING_FORK 1

/* Define to 1 if `vfork' works. */
#define HAVE_WORKING_VFORK 1

/* Define to 1 if you have the X11 library. */
/* #undef HAVE_X11 */

/* Define to the version of the X11 library. */
/* #undef HAVE_X11_VERSION */

/* Define to 1 if you have the <xlocale.h> header file. */
/* #undef HAVE_XLOCALE_H */

/* Define to 1 if you have the zlib compression library. */
/* #undef HAVE_ZLIB */

/* Define to 1 if the system has the type '_Bool'. */
#define HAVE__BOOL 1

/* Defined if libcurl supports AsynchDNS */
/* #undef LIBCURL_FEATURE_ASYNCHDNS */

/* Defined if libcurl supports IDN */
/* #undef LIBCURL_FEATURE_IDN */

/* Defined if libcurl supports IPv6 */
/* #undef LIBCURL_FEATURE_IPV6 */

/* Defined if libcurl supports KRB4 */
/* #undef LIBCURL_FEATURE_KRB4 */

/* Defined if libcurl supports libz */
/* #undef LIBCURL_FEATURE_LIBZ */

/* Defined if libcurl supports NTLM */
/* #undef LIBCURL_FEATURE_NTLM */

/* Defined if libcurl supports SSL */
/* #undef LIBCURL_FEATURE_SSL */

/* Defined if libcurl supports SSPI */
/* #undef LIBCURL_FEATURE_SSPI */

/* Defined if libcurl supports DICT */
/* #undef LIBCURL_PROTOCOL_DICT */

/* Defined if libcurl supports FILE */
/* #undef LIBCURL_PROTOCOL_FILE */

/* Defined if libcurl supports FTP */
/* #undef LIBCURL_PROTOCOL_FTP */

/* Defined if libcurl supports FTPS */
/* #undef LIBCURL_PROTOCOL_FTPS */

/* Defined if libcurl supports HTTP */
/* #undef LIBCURL_PROTOCOL_HTTP */

/* Defined if libcurl supports HTTPS */
/* #undef LIBCURL_PROTOCOL_HTTPS */

/* Defined if libcurl supports IMAP */
/* #undef LIBCURL_PROTOCOL_IMAP */

/* Defined if libcurl supports LDAP */
/* #undef LIBCURL_PROTOCOL_LDAP */

/* Defined if libcurl supports POP3 */
/* #undef LIBCURL_PROTOCOL_POP3 */

/* Defined if libcurl supports RTSP */
/* #undef LIBCURL_PROTOCOL_RTSP */

/* Defined if libcurl supports SMTP */
/* #undef LIBCURL_PROTOCOL_SMTP */

/* Defined if libcurl supports TELNET */
/* #undef LIBCURL_PROTOCOL_TELNET */

/* Defined if libcurl supports TFTP */
/* #undef LIBCURL_PROTOCOL_TFTP */

/* Define to 1 if 'lstat' dereferences a symlink specified with a trailing
   slash. */
#define LSTAT_FOLLOWS_SLASHED_SYMLINK 1

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT "https://github.com/asterisk/asterisk/issues"

/* Define to the full name of this package. */
#define PACKAGE_NAME "asterisk"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "asterisk 23"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "asterisk"

/* Define to the home page for this package. */
#define PACKAGE_URL ""

/* Define to the version of this package. */
#define PACKAGE_VERSION "23"

/* Define to necessary symbol if this constant uses a non-standard name on
   your system. */
/* #undef PTHREAD_CREATE_JOINABLE */

/* Define if your system needs braces around PTHREAD_ONCE_INIT */
/* #undef PTHREAD_ONCE_INIT_NEEDS_BRACES */

/* Name of RADIUS library include header */
/* #undef RADIUS_HEADER_STR */

/* Define to the type of arg 1 for 'select'. */
#define SELECT_TYPE_ARG1 int

/* Define to the type of args 2, 3 and 4 for 'select'. */
#define SELECT_TYPE_ARG234 (fd_set *)

/* Define to the type of arg 5 for 'select'. */
#define SELECT_TYPE_ARG5 (struct timeval *)

/* The size of 'char *', as computed by sizeof. */
#define SIZEOF_CHAR_P 8

/* The size of 'fd_set.fds_bits', as computed by sizeof. */
#define SIZEOF_FD_SET_FDS_BITS 8

/* The size of 'int', as computed by sizeof. */
#define SIZEOF_INT 4

/* The size of 'long', as computed by sizeof. */
#define SIZEOF_LONG 8

/* The size of 'long long', as computed by sizeof. */
#define SIZEOF_LONG_LONG 8

/* If using the C implementation of alloca, define if you know the
   direction of stack growth for your system; otherwise it will be
   automatically deduced at runtime.
	STACK_DIRECTION > 0 => grows toward higher addresses
	STACK_DIRECTION < 0 => grows toward lower addresses
	STACK_DIRECTION = 0 => direction of growth unknown */
/* #undef STACK_DIRECTION */

/* Define to 1 if all of the C89 standard headers exist (not just the ones
   required in a freestanding environment). This macro is provided for
   backward compatibility; new code need not use it. */
#define STDC_HEADERS 1

/* Define to 1 if your <sys/time.h> declares 'struct tm'. */
/* #undef TM_IN_SYS_TIME */

/* Define to a type of the same size as fd_set.fds_bits[[0]] */
#define TYPEOF_FD_SET_FDS_BITS long

/* Enable extensions on AIX, Interix, z/OS.  */
#ifndef _ALL_SOURCE
# define _ALL_SOURCE 1
#endif
/* Enable general extensions on macOS.  */
#ifndef _DARWIN_C_SOURCE
# define _DARWIN_C_SOURCE 1
#endif
/* Enable general extensions on Solaris.  */
#ifndef __EXTENSIONS__
# define __EXTENSIONS__ 1
#endif
/* Enable GNU extensions on systems that have them.  */
#ifndef _GNU_SOURCE
# define _GNU_SOURCE 1
#endif
/* Enable X/Open compliant socket functions that do not require linking
   with -lxnet on HP-UX 11.11.  */
#ifndef _HPUX_ALT_XOPEN_SOCKET_API
# define _HPUX_ALT_XOPEN_SOCKET_API 1
#endif
/* Identify the host operating system as Minix.
   This macro does not affect the system headers' behavior.
   A future release of Autoconf may stop defining this macro.  */
#ifndef _MINIX
/* # undef _MINIX */
#endif
/* Enable general extensions on NetBSD.
   Enable NetBSD compatibility extensions on Minix.  */
#ifndef _NETBSD_SOURCE
# define _NETBSD_SOURCE 1
#endif
/* Enable OpenBSD compatibility extensions on NetBSD.
   Oddly enough, this does nothing on OpenBSD.  */
#ifndef _OPENBSD_SOURCE
# define _OPENBSD_SOURCE 1
#endif
/* Define to 1 if needed for POSIX-compatible behavior.  */
#ifndef _POSIX_SOURCE
/* # undef _POSIX_SOURCE */
#endif
/* Define to 2 if needed for POSIX-compatible behavior.  */
#ifndef _POSIX_1_SOURCE
/* # undef _POSIX_1_SOURCE */
#endif
/* Enable POSIX-compatible threading on Solaris.  */
#ifndef _POSIX_PTHREAD_SEMANTICS
# define _POSIX_PTHREAD_SEMANTICS 1
#endif
/* Enable extensions specified by ISO/IEC TS 18661-5:2014.  */
#ifndef __STDC_WANT_IEC_60559_ATTRIBS_EXT__
# define __STDC_WANT_IEC_60559_ATTRIBS_EXT__ 1
#endif
/* Enable extensions specified by ISO/IEC TS 18661-1:2014.  */
#ifndef __STDC_WANT_IEC_60559_BFP_EXT__
# define __STDC_WANT_IEC_60559_BFP_EXT__ 1
#endif
/* Enable extensions specified by ISO/IEC TS 18661-2:2015.  */
#ifndef __STDC_WANT_IEC_60559_DFP_EXT__
# define __STDC_WANT_IEC_60559_DFP_EXT__ 1
#endif
/* Enable extensions specified by C23 Annex F.  */
#ifndef __STDC_WANT_IEC_60559_EXT__
# define __STDC_WANT_IEC_60559_EXT__ 1
#endif
/* Enable extensions specified by ISO/IEC TS 18661-4:2015.  */
#ifndef __STDC_WANT_IEC_60559_FUNCS_EXT__
# define __STDC_WANT_IEC_60559_FUNCS_EXT__ 1
#endif
/* Enable extensions specified by C23 Annex H and ISO/IEC TS 18661-3:2015.  */
#ifndef __STDC_WANT_IEC_60559_TYPES_EXT__
# define __STDC_WANT_IEC_60559_TYPES_EXT__ 1
#endif
/* Enable extensions specified by ISO/IEC TR 24731-2:2010.  */
#ifndef __STDC_WANT_LIB_EXT2__
# define __STDC_WANT_LIB_EXT2__ 1
#endif
/* Enable extensions specified by ISO/IEC 24747:2009.  */
#ifndef __STDC_WANT_MATH_SPEC_FUNCS__
# define __STDC_WANT_MATH_SPEC_FUNCS__ 1
#endif
/* Enable extensions on HP NonStop.  */
#ifndef _TANDEM_SOURCE
# define _TANDEM_SOURCE 1
#endif
/* Enable X/Open extensions.  Define to 500 only if necessary
   to make mbstate_t available.  */
#ifndef _XOPEN_SOURCE
/* # undef _XOPEN_SOURCE */
#endif


/* Define to 1 if running on Darwin. */
/* #undef _DARWIN_UNLIMITED_SELECT */

/* Number of bits in a file offset, on hosts where this is settable. */
/* #undef _FILE_OFFSET_BITS */

/* Prevent clang array-bounds warning by not using strcmp from bits/string2.h
   */
/* #undef _HAVE_STRING_ARCH_strcmp */

/* Prevent clang array-bounds warning by not using strsep from bits/string2.h
   */
/* #undef _HAVE_STRING_ARCH_strsep */

/* Define to 1 if necessary to make fseeko visible. */
/* #undef _LARGEFILE_SOURCE */

/* Define to 1 on platforms where this makes off_t a 64-bit type. */
/* #undef _LARGE_FILES */

/* Number of bits in time_t, on hosts where this is settable. */
/* #undef _TIME_BITS */

/* Define to 1 on platforms where this makes time_t a 64-bit type. */
/* #undef __MINGW_USE_VC2005_COMPAT */

/* Define to empty if 'const' does not conform to ANSI C. */
/* #undef const */

/* Define curl_free() as free() if our version of curl lacks curl_free. */
/* #undef curl_free */

/* Define as 'int' if <sys/types.h> doesn't define. */
/* #undef gid_t */

/* Define to '__inline__' or '__inline' if that's what the C compiler
   calls it, or to nothing if 'inline' is not supported under any name.  */
#ifndef __cplusplus
/* #undef inline */
#endif

/* Define to 'int' if <sys/types.h> does not define. */
/* #undef mode_t */

/* Define to 'long int' if <sys/types.h> does not define. */
/* #undef off_t */

/* Define as a signed integer type capable of holding a process identifier. */
/* #undef pid_t */

/* Define as 'unsigned int' if <stddef.h> doesn't define. */
/* #undef size_t */

/* Define as 'int' if <sys/types.h> doesn't define. */
/* #undef uid_t */

/* Define as `fork' if `vfork' does not work. */
/* #undef vfork */

/* Define to empty if the keyword 'volatile' does not work. Warning: valid
   code using 'volatile' can become incorrect without. Disable with care. */
/* #undef volatile */

#endif	/* ASTERISK_AUTOCONFIG_H */
