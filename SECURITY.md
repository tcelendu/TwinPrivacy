# Security considerations

TwinPrivacy is a research prototype evaluating *provided structured
disclosure records*. It is not a clinically deployed system, an access
control mechanism, or a guarantee of patient-data security.

The hash-linked record checks detect certain modifications when an original
trusted digest is retained independently. They cannot prove every access
was logged, identify the recording organization, or prevent replacement of
both a log and an untrusted local anchor.

**Do not upload real patient information, credentials, or sensitive logs to
this public repository.** Use the included generated data to reproduce
the published computational experiments.

To report a security concern, use the repository's private vulnerability
reporting feature after it has been enabled by the repository owner.
Do not publish an exploitable vulnerability with private data attached.
