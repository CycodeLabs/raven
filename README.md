# Raven - CI/CD Security Analyzer
[![License](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](https://opensource.org/licenses/MIT)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/CycodeLabs/raven?color=red)
[<img src="https://img.shields.io/badge/Protected%20By%20Cimon%20-none.svg?color=8831de&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGcgY2xpcC1wYXRoPSJ1cmwoI2NsaXAwXzMyOTRfMTI0MDIpIj4KPHBhdGggZD0iTTQyLjcyNTcgNDMuOTczMkM0MS43Njc1IDQzLjQxNDIgNDEuMDIyMyA0Mi41NTYzIDQwLjIxMDUgNDEuNzYzNEw0MC4yMzA0IDM5LjI2NzhMNDQuMTc2MyAzNS4xODYzQzQ0LjcyODYgMzQuNjE0NCA0NC4zMDI3IDMyLjk2MzYgMzkuNjcxNSAzMi45NjM2QzM0LjA1NTQgMzIuOTYzNiAzMy42ODk1IDM0LjgxNTkgMzQuMzE0OSAzNS4zNjgzTDM4Ljc2NjUgMzkuMjkzOEwzOC43NDY2IDQxLjgzNDlDMzYuNDkwOCA0My4yODQyIDMyLjU1ODMgNDUuOTU1NCAzMC43OTQ5IDQzLjk2NjdDMzEuNTIwMiA0NS41Nzg0IDMzLjMxMDIgNDUuNTkxNCAzNS4xNjY3IDQ1LjAxOTVDMzUuMzUzIDQ1LjE4ODUgMzUuNjI1OCA0NS40MTYgMzUuOTY1MiA0NS42MzY5VjQ2LjgzMjhDMzUuOTY1MiA0Ny43NjIxIDM2Ljc0MzcgNDguNTIyNSAzNy42OTUyIDQ4LjUyMjVINDAuNTg5OEM0MS41NDEzIDQ4LjUyMjUgNDIuMzE5OCA0Ny43Njg2IDQyLjMxOTggNDYuODQ1OEw0Mi4zNDY0IDQ1LjU5NzlDNDIuNjE5MyA0NS40MjI1IDQyLjg5ODcgNDUuMjI3NSA0My4xODQ5IDQ1QzQ0LjE4OTYgNDUuMTIzNSA0NS4xNDc4IDQ0LjcyMDYgNDUuODMzMiA0My4zMjk3QzQ0Ljk2ODIgNDQuMTg3NiA0My44MTAzIDQ0LjY2MjEgNDIuNzMyNCA0My45NzMySDQyLjcyNTdaTTQxLjMyODQgNDYuMTM3NEw0MS4zMTUxIDQ2LjgzOTNDNDEuMzE1MSA0Ny4yMjkyIDQwLjk4OSA0Ny41NTQyIDQwLjU4MzEgNDcuNTU0MkgzNy42ODg2QzM3LjI4OTMgNDcuNTU0MiAzNi45NTY2IDQ3LjIzNTcgMzYuOTU2NiA0Ni44MzkzVjQ0LjE2MTZMMzkuNDM4NiA0Mi42ODYzTDQxLjM3NDkgNDQuMjUyNkw0MS4zMzUgNDYuMTM3NEg0MS4zMjg0WiIgZmlsbD0iIzBDMEMwQyIvPgo8cGF0aCBkPSJNMzIuOTA0IDMxLjYzMTNDMzEuMjI3MiAzMC42OTU0IDI2LjkxNTQgMzEuMzA2NCAyNi45MTU0IDMxLjMwNjRDMjYuOTE1NCAzMS4zMDY0IDI3LjcxMzggMjYuMzk5NSAyNC4xMjA2IDI2LjM5OTVDMjAuNTI3NCAyNi4zOTk1IDE5LjgxNTQgMzAuMDU4NSAxOS44MTU0IDMxLjQ2MjNDMTkuODE1NCAzMi44NjYxIDIxLjA5MyAzNC40MjU5IDI1LjMxODQgMzIuNzg4MkMyOS41NDM3IDMxLjE1MDQgMzIuOTA0IDMxLjYzMTMgMzIuOTA0IDMxLjYzMTNaTTI0LjExNCAzMC4wMzlDMjMuNDA4NiAzMC4wMzkgMjIuODQzIDI5LjQ4MDEgMjIuODQzIDI4Ljc5NzdDMjIuODQzIDI4LjExNTMgMjMuNDE1MyAyNy41NTY0IDI0LjExNCAyNy41NTY0QzI0LjgxMjcgMjcuNTU2NCAyNS4zODQ5IDI4LjExNTMgMjUuMzg0OSAyOC43OTc3QzI1LjM4NDkgMjkuNDgwMSAyNC44MTI3IDMwLjAzOSAyNC4xMTQgMzAuMDM5WiIgZmlsbD0iIzBDMEMwQyIvPgo8cGF0aCBkPSJNNDYuNDI1MiAyNi40MDZDNDMuODM2OCAyNi40MDYgNDQuNDA5IDMxLjMxMjkgNDQuNDA5IDMxLjMxMjlDNDQuNDA5IDMxLjMxMjkgNDEuOTMzNyAzMC43NjY5IDQwLjcyMjcgMzEuNzAyOEM0MC43MjI3IDMxLjcwMjggNDIuNTg1OCAzMS4zMzIzIDQ1LjczMzIgMzIuNzk0N0M0OC4xMzUzIDMzLjkxMjUgNDkuODI1NSAzMi40MTc3IDQ5LjcwNTcgMzEuNDY4OEM0OS41MzI3IDMwLjA3OCA0OS4wMjAzIDI2LjQwNiA0Ni40MjUyIDI2LjQwNlpNNDcuMTkwNCAzMC4xNjlDNDYuNTQ1IDMwLjE2OSA0Ni4wMTkzIDI5LjY1NTYgNDYuMDE5MyAyOS4wMjUyQzQ2LjAxOTMgMjguMzk0NyA0Ni41NDUgMjcuODgxMyA0Ny4xOTA0IDI3Ljg4MTNDNDcuODM1OSAyNy44ODEzIDQ4LjM2MTYgMjguMzk0NyA0OC4zNjE2IDI5LjAyNTJDNDguMzYxNiAyOS42NTU2IDQ3LjgzNTkgMzAuMTY5IDQ3LjE5MDQgMzAuMTY5WiIgZmlsbD0iIzBDMEMwQyIvPgo8cGF0aCBkPSJNNTUuNTgxOCAzMC41OTE1QzU1LjEwOTQgMjkuOTgwNiA1My42ODU0IDI2LjU0MjYgNTIuNzkzNyAyMy45OTQ5QzUzLjkyNDkgMjIuNzY2NiA1NS4zMjg5IDIwLjc4NDMgNTYuMTQwNyAxOC41ODExQzU3LjMwNTIgMTUuNDI5IDU2LjcxMyAxMi44MDM0IDU0LjkyMyAxMC41Njc3QzUwLjg0NDEgNS40NzIzNiA0Ni4wNDY1IDguMDU5MDIgNDQuMDYzNSA5LjI5Mzg1QzQwLjIxMDggNy4wMDYxNiAzNC4xNzU2IDQuNjAxNDggMjYuMzMwNCA1LjEzNDQxQzI3LjEyODkgNC4xMjcwNCAyOC4zMDY2IDIuNjY0NzQgMjkuMzk3OSAxLjM2NDkxTDMwLjU0MjQgMC4wMDY1OTE4TDI4Ljc2NTggMC4zMTg1NUMyMS44OTg3IDEuNTE0MzkgMTYuNjM1NCA2LjA5NjI4IDE1LjIxMTQgNy40NDgxQzE0LjAxMzYgNi44MDQ2OSAxMC43MTk5IDUuMjgzODkgNy40NzI2NiA2LjAxODI5QzUuNTAzMDUgNi40NjY3MyAzLjkwNjA3IDcuNjY5MDcgMi43MjE2NCA5LjU3OTgxQy0wLjAwNjU0MzAxIDEzLjk5OTIgMC44MzE4NzMgMTguODE1MSA1LjIyMzU4IDIzLjg3MTRDLTUuMzQzMTMgMzguNzAyNCAzLjM2NzA4IDQ2LjgxMzMgMy40NTM1OSA0Ni44OTEzTDQuNjI0NzEgNDcuOTQ0Mkw0LjU2NDgyIDQ2LjM4NDRDNC41NjQ4MiA0Ni4zODQ0IDQuNTUxNTEgNDYuMDc4OSA0LjU0NDg2IDQ1LjQ4NzVDNy40OTI2MyA0OS40NTIgMTEuNjg0NyA1MS45OTk3IDExLjg5MSA1Mi4xMjMxQzExLjg5MSA1Mi4xMjMxIDcuMTAwMDMgNDcuNjcxMiA0LjQ1MTcgNDIuOTI2OUwzLjIwNzM5IDQwLjY5MTJWNDMuMjMyM0MzLjIwMDczIDQzLjcxOTggMy4yMDczOSA0NC4xNTUyIDMuMjA3MzkgNDQuNTMyMkMxLjM3MDg2IDQxLjc3IC0xLjI1NzUxIDM0Ljk2NTQgNi42MDc2MyAyNC4yMDI5TDYuOTA3MDYgMjMuNzkzNEw2LjM4MTM5IDIzLjE5NTVDNC44NTA5NSAyMS40NjAyIDAuMTkzMDggMTYuMTgyOSAzLjg1OTQ5IDEwLjIzNjJDNC44NDQyOSA4LjYzNzQ0IDYuMTYxODEgNy42MzY1NyA3Ljc2NTQ0IDcuMjcyNjJDMTEuMTk5IDYuNDg2MjMgMTQuOTE4NiA4Ljc2NzQyIDE0Ljk1ODUgOC43OTM0MkwxNS40MjQzIDkuMDc5MzhMMTUuODAzNiA4LjY4OTQzQzE1Ljg1NjggOC42Mzc0NCAyMC42MTQ1IDMuODA4NTggMjcuMTU1NSAxLjk5NTMzQzI1Ljc5OCAzLjY1OTEgMjQuNTYwNCA1LjIyNTQgMjQuMzQwOCA1LjUyNDM2TDIzLjQzNTggNi43MjY3TDI0Ljk1MyA2LjU1MTIyQzI2LjYzNjUgNi4zNTYyNCAyOC4yNDAxIDYuMzEwNzUgMjkuNzU3MiA2LjM3NTc0QzMyLjQ3MjEgOC4yMDIgMzcuNjA5MSAxMC45NDQ2IDM4LjY2NzEgMTkuMjExNUMzOC42NjcxIDE5LjIxMTUgNDEuMTM1NyAxMy45NzMyIDM4LjYxMzggOC4xMzA1MUM0MC42MTY3IDguODcxNDEgNDIuMzI2OCA5Ljc0ODc5IDQzLjcxMDkgMTAuNTkzN0w0NC4wNzAyIDEwLjgxNDZMNDQuNDI5NSAxMC41ODcyQzQ3LjE1MSA4Ljg1MTkxIDUwLjY4NDQgNy4zNjM2MSA1My44NzE3IDExLjM0NzZDNTcuMzU4NCAxNS43MDg1IDUzLjQ1MjUgMjEuNDQwNyA1MS41NTYxIDIzLjM3MUw1MS4yNzY2IDIzLjY1NjlMNTEuNDAzIDI0LjAyNzRDNTEuOTQ4NyAyNS42MzI3IDUzLjgwNTEgMzAuNTg1IDU0LjYxNyAzMS40ODE5TDU0LjcxMDEgMzEuNTY2NEM1NC45NTYzIDMxLjc0ODQgNjAuMDggMzUuNjg2OCA1OC4zMjMzIDQxLjA5NDFDNTcuODU3NSAzOC42MjQ0IDU0LjQ3MDYgMzUuODY4OCA1NC40NzA2IDM1Ljg2ODhDNTcuNjQ0NiA0Mi4wNjkgNTUuNjg4MyA0NS45NjIgNTMuMDM5OSA0OS41NDNDNTMuMDM5OSA0OS41NDMgNTYuMzI3MSA0Ny42OTcyIDU3LjMyNTIgNDIuODI5NEM1Ny44MDQzIDQzLjYwOTMgNTcuNDUxNiA0NS40NzQ1IDU3LjQ1MTYgNDUuNDc0NUw1OC41Mjk2IDQzLjcyNjNDNjIuMTU2IDM3Ljg3MDUgNTguMjE2OCAzMi41OTMyIDU1LjU3NTEgMzAuNTcyTDU1LjU4MTggMzAuNTkxNVoiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik01MC4yNTE4IDE1LjgzODRDNTAuNTY0NSAxNi4zOTc0IDUwLjcwNDMgMTYuOTg4OCA1MC43MjQyIDE3LjU2MDdDNTEuMjIzMyAxNi41NzkzIDUyLjA4MTcgMTQuMzgyNiA1MC43OTA4IDEyLjg0ODhDNDkuNjk5NSAxMS41NTU1IDQ3LjU4MzUgMTIuNTM2OSA0Ni45NTggMTMuNTExN0M0OC4xNDkxIDEzLjQ3OTIgNDkuNTU5OCAxNC41OTcxIDUwLjI0NTEgMTUuODMxOUw1MC4yNTE4IDE1LjgzODRaIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNMTMuMTY4NSAxMi4zMjg5QzEzLjIzNSAxMi4zNDg0IDEzLjMwMTYgMTIuMzY3OSAxMy4zNjE1IDEyLjM5MzlDMTIuOTM1NiAxMS4zODY1IDEyLjE1MDQgMTAuNjI2MSAxMS4xMTkgMTAuMzU5N0M5LjEzNjEyIDkuODUyNzIgNy4wMTM0NiAxMS4zNjcgNi4zNzQ2NyAxMy43MzkyQzUuNzM1ODggMTYuMTE3OSA2LjgyMDUgMTguNDU3NiA4Ljc5Njc2IDE4Ljk2NDVDOC44MzAwMyAxOC45NzEgOC44Njk5NiAxOC45Nzc1IDguOTAzMjMgMTguOTg0QzguMzI0MzIgMTguMDI4NiA4LjEzMTM1IDE2Ljc3NDMgOC40NzA3MSAxNS41MTM1QzkuMDgyODkgMTMuMjQ1MyAxMS4xODU2IDExLjgyMiAxMy4xNjE5IDEyLjMyODlIMTMuMTY4NVoiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik01Mi45NzI5IDQxLjI0MzVDNTMuMzU4OSA0MS40NjQ1IDU0LjQzNjggNDIuMzQ4NCA1NC40NzY4IDQ0Ljk0MTVDNTUuNjgxMiA0MS4wNDg2IDUzLjA0NjEgMzYuNDA4MiA1Mi44NzMxIDM0LjQzODlDNTUuMDIyNCAzNC40Mzg5IDU3LjA5ODUgMzYuNjAzMiA1Ny41MDQ0IDM3LjI4NTZDNTYuMDMzOCAzMS45NjI4IDUwLjQzNzcgMzIuMDM0MyA1MC40Mzc3IDMyLjAzNDNDNTAuNDM3NyAzMi4wMzQzIDUyLjMyNzUgMzEuNjYzOCA1Mi41NDcxIDMxLjIxNTRDNTEuMjQ5NSAyOS4yOTE2IDQ5Ljc5MjMgMjQuNTQwOCA0OS40NzI5IDIzLjU2NTlDNDkuMTUzNSAyMi41OTEgNDguNDI4MiAyMC43NjQ4IDQ3LjA3MDggMjAuNzY0OEM0NS43MTMzIDIwLjc2NDggNDEuOTUzOCAyOS45NzQgMzguNzUzMSAyOS45NzRDMzUuNTUyNSAyOS45NzQgMzEuMTYwOCAyNS44OTkxIDMxLjE2MDggMjUuODk5MUMzMS4xNjA4IDI1Ljg5OTEgMjUuMjY1MyAxOS43NTc0IDIwLjI5NDcgMjEuMTg3MkMxNS4zMjQxIDIyLjYxNyAxNC41ODU0IDI4LjI4NDMgMTQuNjMyIDMyLjYxMjdDMTcuMDAwOSAzMi4wNzk4IDE4LjUwNDcgMzIuODQwMiAxOC41MDQ3IDMyLjg0MDJDMTEuNjM3NyAzMy41ODExIDkuMDIyNjIgMzcuNSA5LjEyOTA5IDM5LjExODNDOS45NDA4OSAzOC4zNjQ0IDEyLjgxNTUgMzcuNTMyNSAxNC4yNTI3IDM3LjIwNzZDNy42OTg0NiA0Mi44ODc4IDExLjcwNDIgNDguODY3IDEzLjc4MDMgNTAuODQyOEMxMi42MDkyIDQ1LjY5NTQgMTMuODczNSA0My4zMjMzIDEzLjg3MzUgNDMuMzIzM0MxMy44NzM1IDQzLjMyMzMgMTMuNzAwNSA0Ni40MTY5IDE2LjM4MjEgNDkuMjYzNUMyMi43MjM0IDU1Ljc0MzEgNDcuMjcwNCA1NS44OTI2IDUyLjgzOTkgNDcuNjMyMkM1NC4wMzc2IDQ1Ljg1NzkgNTMuNTMxOSA0My4xMjE4IDUyLjk3OTYgNDEuMjU2NUw1Mi45NzI5IDQxLjI0MzVaTTE5LjgxNTYgMzEuNDY4OEMxOS44MTU2IDMwLjA2NSAyMC41MzQyIDI2LjQwNiAyNC4xMjA4IDI2LjQwNkMyNy43MDczIDI2LjQwNiAyNi45MTU1IDMxLjMxMjkgMjYuOTE1NSAzMS4zMTI5QzI2LjkxNTUgMzEuMzEyOSAzMS4yMzQgMzAuNzAxOSAzMi45MDQyIDMxLjYzNzhDMzIuOTA0MiAzMS42Mzc4IDI5LjU0MzkgMzEuMTU2OSAyNS4zMTg1IDMyLjc5NDdDMjEuMDkzMiAzNC40MzI0IDE5LjgxNTYgMzIuODcyNyAxOS44MTU2IDMxLjQ2ODhaTTQzLjE4NDggNDUuMDA2NUM0Mi44OTg2IDQ1LjIzNCA0Mi42MjU4IDQ1LjQyOSA0Mi4zNDYzIDQ1LjYwNDVMNDIuMzE5NyA0Ni44NTIzQzQyLjMxOTcgNDcuNzc1MiA0MS41NDc5IDQ4LjUyOTEgNDAuNTg5NyA0OC41MjkxSDM3LjY5NTFDMzYuNzQzNiA0OC41MjkxIDM1Ljk2NTEgNDcuNzc1MiAzNS45NjUxIDQ2LjgzOTNWNDUuNjQzNUMzNS42MjU3IDQ1LjQyMjUgMzUuMzU5NSA0NS4xOTUgMzUuMTY2NiA0NS4wMjZDMzMuMzEwMSA0NS41OTggMzEuNTIwMSA0NS41Nzg1IDMwLjc5NDggNDMuOTczMkMzMi41NTgyIDQ1Ljk2ODQgMzYuNDkwNyA0My4yOTA4IDM4Ljc0NjUgNDEuODQxNUwzOC43NjY0IDM5LjMwMDNMMzQuMzE0OCAzNS4zNzQ4QzMzLjY4OTQgMzQuODIyNCAzNC4wNTUzIDMyLjk3MDEgMzkuNjcxNCAzMi45NzAxQzQ0LjMwOTMgMzIuOTcwMSA0NC43Mjg1IDM0LjYyMDkgNDQuMTc2MiAzNS4xOTI4TDQwLjIzMDMgMzkuMjc0M0w0MC4yMTA0IDQxLjc3QzQxLjAyMjIgNDIuNTYyOSA0MS43Njc0IDQzLjQyMDcgNDIuNzI1NiA0My45Nzk3QzQzLjgwMzYgNDQuNjY4NiA0NC45NjE0IDQ0LjE5NDEgNDUuODI2NCA0My4zMzYzQzQ1LjEzNDQgNDQuNzI3MSA0NC4xODI5IDQ1LjEzIDQzLjE3ODEgNDUuMDA2NUg0My4xODQ4Wk00NS43MzMzIDMyLjc5NDdDNDIuNTg1OSAzMS4zMzg5IDQwLjcyMjcgMzEuNzAyOCA0MC43MjI3IDMxLjcwMjhDNDEuOTMzOCAzMC43NjY5IDQ0LjQwOTEgMzEuMzEyOSA0NC40MDkxIDMxLjMxMjlDNDQuNDA5MSAzMS4zMTI5IDQzLjgzMDIgMjYuNDA2IDQ2LjQyNTMgMjYuNDA2QzQ5LjAyMDQgMjYuNDA2IDQ5LjUzMjggMzAuMDc4IDQ5LjcwNTggMzEuNDY4OEM0OS44MjU2IDMyLjQxNzcgNDguMTM1NCAzMy45MDYgNDUuNzMzMyAzMi43OTQ3WiIgZmlsbD0id2hpdGUiLz4KPHBhdGggZD0iTTI0LjExNDcgMjcuNTU2NEMyMy40MDkzIDI3LjU1NjQgMjIuODQzOCAyOC4xMTUzIDIyLjg0MzggMjguNzk3N0MyMi44NDM4IDI5LjQ4MDEgMjMuNDE2IDMwLjAzOSAyNC4xMTQ3IDMwLjAzOUMyNC44MTM0IDMwLjAzOSAyNS4zODU2IDI5LjQ4MDEgMjUuMzg1NiAyOC43OTc3QzI1LjM4NTYgMjguMTE1MyAyNC44MTM0IDI3LjU1NjQgMjQuMTE0NyAyNy41NTY0WiIgZmlsbD0id2hpdGUiLz4KPHBhdGggZD0iTTQ3LjE5MDYgMzAuMTY5QzQ3LjgzNzQgMzAuMTY5IDQ4LjM2MTggMjkuNjU2OSA0OC4zNjE4IDI5LjAyNTJDNDguMzYxOCAyOC4zOTM0IDQ3LjgzNzQgMjcuODgxMyA0Ny4xOTA2IDI3Ljg4MTNDNDYuNTQzOSAyNy44ODEzIDQ2LjAxOTUgMjguMzkzNCA0Ni4wMTk1IDI5LjAyNTJDNDYuMDE5NSAyOS42NTY5IDQ2LjU0MzkgMzAuMTY5IDQ3LjE5MDYgMzAuMTY5WiIgZmlsbD0id2hpdGUiLz4KPHBhdGggZD0iTTM2Ljk1NjkgNDQuMTYxNlY0Ni44MzkzQzM2Ljk1NjkgNDcuMjI5MiAzNy4yODI5IDQ3LjU1NDIgMzcuNjg4OCA0Ny41NTQySDQwLjU4MzNDNDAuOTgyNiA0Ny41NTQyIDQxLjMxNTMgNDcuMjM1NyA0MS4zMTUzIDQ2LjgzOTNMNDEuMzI4NiA0Ni4xMzc0TDQxLjM2ODUgNDQuMjUyNkwzOS40MzIyIDQyLjY4NjNMMzYuOTUwMiA0NC4xNjE2SDM2Ljk1NjlaIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNMzEuMjU0MiA1NS40MzExQzMxLjI1NDIgNTUuNDMxMSAzMC41OTU0IDU4LjQ5ODcgMjcuMTU1MyA1OS43NzI1QzMyLjU3ODQgNjAuMjA4IDM2Ljk4MzQgNjAuMDMyNSAzOC43NDAxIDU5LjAxMjFDMzkuNTY1MiA1Ny40OTc4IDQwLjYyMzIgNTQuODcyMiA0MC42MjMyIDU0Ljg3MjJDMzUuODkyMSA1Ni4zNzM1IDMxLjI1NDIgNTUuNDI0NiAzMS4yNTQyIDU1LjQyNDZWNTUuNDMxMVoiIGZpbGw9IndoaXRlIi8+CjwvZz4KPGRlZnM+CjxjbGlwUGF0aCBpZD0iY2xpcDBfMzI5NF8xMjQwMiI+CjxyZWN0IHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgZmlsbD0id2hpdGUiLz4KPC9jbGlwUGF0aD4KPC9kZWZzPgo8L3N2Zz4K">](https://cimon.build/)

**RAVEN (Risk Analysis and Vulnerability Enumeration for CI/CD)** is a powerful security tool designed to perform massive scans for GitHub Actions CI workflows and digest the discovered data into a Neo4j database.
<br><br><br>
<p align="center">
<img src="assets/images/logo.png" alt="Raven" width="250" height="250" alig=center>
</p>
<br><br>


With Raven, we were able to identify and report security vulnerabilities in some of the most popular repositories hosted on GitHub, including:

- [FreeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp) (the most popular project on GitHub)
- [Storybook](https://github.com/storybookjs/storybook) (One of the most popular frontend frameworks)
- [Fluent UI](https://github.com/microsoft/fluentui) by Microsoft
- and much more

We listed all vulnerabilities discovered using Raven in the tool [Hall of Fame](#hall-of-fame---vulnerabilities-found-and-disclosed-using-raven).

## What is Raven

The tool provides the following capabilities to scan and analyze potential CI/CD vulnerabilities:

- ⏬ **Downloader:** You can download workflows and actions necessary for analysis. Workflows can be downloaded for a specified organization or for all repositories, sorted by star count. Performing this step is a prerequisite for analyzing the workflows.
- 📊 **Indexer:** Digesting the downloaded data into a graph-based Neo4j database. This process involves establishing relationships between workflows, actions, jobs, steps, etc.
- 📚 **Query Library:** We created a library of pre-defined queries based on research conducted by the community.
- ❗ **Report:** Raven has a simple way of reporting suspicious findings. As an example, it can be incorporated into the CI process for pull requests and run there.

Possible usages for Raven:

- Scanner for your own organization's security
- Scanning specified organizations for bug bounty purposes
- Scan everything and report issues found to save the internet
- Research and learning purposes

This tool provides a reliable and scalable solution for CI/CD security analysis, enabling users to query bad configurations and gain valuable insights into their codebase's security posture.

## Why Raven

In the past year, Cycode Labs conducted extensive research on fundamental security issues of CI/CD systems. We examined the depths of many systems, thousands of projects, and several configurations. The conclusion is clear – the model in which security is delegated to developers has failed. This has been proven several times in our previous content:

- A simple injection scenario exposed dozens of public repositories, including popular open-source projects.
- We found that one of the most popular frontend frameworks was vulnerable to the innovative method of branch injection attack.
- We detailed a completely different attack vector, 3rd party integration risks, the most popular project on GitHub, and thousands more.
- Finally, the Microsoft 365 UI framework, with more than 300 million users, is vulnerable to an additional new threat – an artifact poisoning attack.
- Additionally, we found, reported, and disclosed hundreds of other vulnerabilities privately.

Each of the vulnerabilities above has unique characteristics, making it nearly impossible for developers to stay up to date with the latest security trends. Unfortunately, each vulnerability shares a commonality – each exploitation can impact millions of victims.

It was for these reasons that Raven was created, a framework for CI/CD security analysis workflows (and GitHub Actions as the first use case). In our focus, we examined complex scenarios where each issue isn't a threat on its own, but when combined, they pose a severe threat.

## Setup && Run

To get started with Raven, follow these installation instructions:

**Step 1**: Download the latest stable version, The install script requires `curl`, `wget` and `jq`
``` bash
curl -sSfL https://raw.githubusercontent.com/CycodeLabs/raven/f020094d175ab5cd0eb10442c6f7728485cc6903/install.sh | bash
cd raven
```

or, you can download the latest release from `https://github.com/CycodeLabs/raven/releases/latest`

**Step 2**: Create virtual environment
``` bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 3**: Build containerized environment and install Raven
```bash
sudo make setup
```

**Step 4**: Run Raven
``` bash
raven
```

### Prerequisites

- Python 3.9+
- Docker Compose v2.1.0+
- Docker Engine v1.13.0+

## Infrastructure
Raven is using two primary docker containers: Redis and Neo4j. 
`make setup` will run a `docker-compose` command to prepare that environment.

![Infrastructure](assets/images/infrastructure.png)


## Usage

The tool contains two main functionalities, `download` and `index`.

### Download


#### Download Organization Repositories

```bash
usage: raven download org [-h] --token TOKEN [--debug] [--redis-host REDIS_HOST] [--redis-port REDIS_PORT] [--clean-redis] --org-name ORG_NAME

options:
  -h, --help            show this help message and exit
  --token TOKEN         GITHUB_TOKEN to download data from Github API (Needed for effective rate-limiting)
  --debug               Whether to print debug statements, default: False
  --redis-host REDIS_HOST
                        Redis host, default: localhost
  --redis-port REDIS_PORT
                        Redis port, default: 6379
  --clean-redis, -cr    Whether to clean cache in the redis, default: False
  --org-name ORG_NAME   Organization name to download the workflows
```

#### Download Public Repositories
``` bash
usage: raven download crawl [-h] --token TOKEN [--debug] [--redis-host REDIS_HOST] [--redis-port REDIS_PORT] [--clean-redis] [--max-stars MAX_STARS] [--min-stars MIN_STARS]

options:
  -h, --help            show this help message and exit
  --token TOKEN         GITHUB_TOKEN to download data from Github API (Needed for effective rate-limiting)
  --debug               Whether to print debug statements, default: False
  --redis-host REDIS_HOST
                        Redis host, default: localhost
  --redis-port REDIS_PORT
                        Redis port, default: 6379
  --clean-redis, -cr    Whether to clean cache in the redis, default: False
  --max-stars MAX_STARS
                        Maximum number of stars for a repository
  --min-stars MIN_STARS
                        Minimum number of stars for a repository, default: 1000
```

### Index

```bash
usage: raven index [-h] [--redis-host REDIS_HOST] [--redis-port REDIS_PORT] [--clean-redis] [--neo4j-uri NEO4J_URI] [--neo4j-user NEO4J_USER] [--neo4j-pass NEO4J_PASS]
                   [--clean-neo4j] [--debug]

options:
  -h, --help            show this help message and exit
  --redis-host REDIS_HOST
                        Redis host, default: localhost
  --redis-port REDIS_PORT
                        Redis port, default: 6379
  --clean-redis, -cr    Whether to clean cache in the redis, default: False
  --neo4j-uri NEO4J_URI
                        Neo4j URI endpoint, default: neo4j://localhost:7687
  --neo4j-user NEO4J_USER
                        Neo4j username, default: neo4j
  --neo4j-pass NEO4J_PASS
                        Neo4j password, default: 123456789
  --clean-neo4j, -cn    Whether to clean cache, and index from scratch, default: False
  --debug               Whether to print debug statements, default: False
```

### Report - beta version
<details>
  <summary>expand</summary>
    
```bash
usage: raven report [-h] [--redis-host REDIS_HOST]
      [--redis-port REDIS_PORT] [--clean-redis]
      [--neo4j-uri NEO4J_URI]
      [--neo4j-user NEO4J_USER]
      [--neo4j-pass NEO4J_PASS] [--clean-neo4j]
      [--slack] [--slack-token SLACK_TOKEN]
        [--channel-id CHANNEL_ID]

optional arguments:
-h, --help            show this help message and exit
--redis-host REDIS_HOST
                    Redis host, default: localhost
--redis-port REDIS_PORT
                    Redis port, default: 6379
--clean-redis, -cr    Whether to clean cache in the redis,
                    default: False
--neo4j-uri NEO4J_URI
                    Neo4j URI endpoint, default:
                    neo4j://localhost:7687
--neo4j-user NEO4J_USER
                    Neo4j username, default: neo4j
--neo4j-pass NEO4J_PASS
                    Neo4j password, default: 123456789
--clean-neo4j, -cn    Whether to clean cache, and index from
                    scratch, default: False
--slack, -s           Send report to slack channel, default:
                    False
--slack-token SLACK_TOKEN, -st SLACK_TOKEN
                    Send report to slack channel
--channel-id CHANNEL_ID, -ci CHANNEL_ID
                    Send report to slack channel
```

  
</details>


## Examples

Retrieve all workflows and actions associated with the organization.
``` bash
raven download org --token $GITHUB_TOKEN --org-name microsoft --org-name google --debug
```

Scrape all publicly accessible GitHub repositories.
``` bash
raven download crawl --token $GITHUB_TOKEN --min-stars 100 --max-stars 1000 --debug
```

After finishing the download process or if interrupted using Ctrl+C, proceed to index all workflows and actions into the Neo4j database.

``` bash
raven index --debug
```

## Rate Limiting

For effective rate limiting, you should supply a Github token.
For authenticated users, the next rate limiting applies:

- Code search - 30 queries per minute
- Any other API - 5000 per hour

## Functionalities

### Downloader

- If the workflow contains an action, the downloader will also download it.
- If the workflow references a reusable workflow, the downloader will also download it.

### Indexer

- If the indexer finds workflow uses an action, it will create a proper connection to it in the graph
- Same applies to reusable workflows
- Same applies to workflow triggered through `workflow_call`

## Knowledge Base

- [Issue Injections](/docs/Issue%20Injections/README.md)
- [Pull Request Injections](/docs/Pull%20Request%20Injections/README.md)
- [Workflow Run Injections](/docs/Multi%20Prerequisite%20Exploits/README.md)
- [CodeSee Injections](/docs/Codesee%20Injections/README.md)

## Current Limitations

- It is possible to run external action by referencing a folder with a `Dockerfile` (without `action.yml`). Currently, this behavior isn't supported.
- It is possible to run external action by referencing a docker container through the `docker://...` URL. Currently, this behavior isn't supported.
- It is possible to run an action by referencing it locally. This creates complex behavior, as it may come from a different repository that was checked out previously. The current behavior is trying to find it in the existing repository.
- We aren't modeling the entire workflow structure. If additional fields are needed, please submit a pull request according to the [contribution](#contribution) guidelines.

## Future Research Work

- Implementation of taint analysis. Example use case - a user can pass a pull request title (which is controllable parameter) to an action parameter that is named `data`. That action parameter may be used in a run command: `- run: echo ${{ inputs.data }}`, which creates a path for a code execution.
- Expand the research for findings of harmful misuse of `GITHUB_ENV`. This may utilize the previous taint analysis as well.
- Research whether `actions/github-script` has an interesting threat landscape. If it is, it can be modeled in the graph.

## Contributing

We encourage contributions from the community to help improve our tooling and research. We manage contributions primarily through GitHub Issues and Pull Requests.

If you have a feature request, bug report, or any improvement suggestions, please create an issue to discuss it. To start contributing, you may check [good first issue](https://github.com/CycodeLabs/Raven/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label to get started quickly into the code base.

To contribute code changes, fork our repository, make your modifications, and then submit a pull request.

Feel free to reach out to the development team through research@cycode.com. We appreciate your collaboration and look forward to your valuable contributions!

## License

[Apache License 2.0](./LICENSE.md)

## Hall of Fame - Vulnerabilities Found and Disclosed Using Raven

| Name                                                                                            | Stars                                                                         | Fix                                                                                                                             | Additional Sources                                                                                           |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp)                       | ![](https://img.shields.io/github/stars/freeCodeCamp/freeCodeCamp)            | CodeSee package update, [0871341](https://github.com/freeCodeCamp/freeCodeCamp/commit/0871341c9cbf96ab455bc3e0bce636e2ef2a2be2) | [Blog](https://cycode.com/blog/cycode-secures-thousands-of-open-source-projects/)                            |
| [storybookjs/storybook](https://github.com/storybookjs/storybook)                               | ![](https://img.shields.io/github/stars/storybookjs/storybook)                | [ffb8558](https://github.com/storybookjs/storybook/commit/ffb8558b7e5df4644299e5ec7009ade6ca1a721c)                             | [Blog](https://cycode.com/ci-story-how-we-found-critical-vulnerabilities-in-storybook-project/)              |
| [tiangolo/fastapi](https://github.com/tiangolo/fastapi)                                         | ![](https://img.shields.io/github/stars/tiangolo/fastapi)                     | [9efab1b](https://github.com/tiangolo/fastapi/commit/9efab1bd96ef061edf1753626573a0a2be1eef09)                                  | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7011753940283203584/)                        |
| [withastro/astro](https://github.com/withastro/astro)                                           | ![](https://img.shields.io/github/stars/withastro/astro)                      | [650fb1a](https://github.com/withastro/astro/commit/650fb1aa51a1c843c10bc89a11732b45a6345b00)                                   | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |
| [statelyai/xstate](https://github.com/statelyai/xstate)                                         | ![](https://img.shields.io/github/stars/statelyai/xstate)                     | CodeSee package update                                                                                                          | [Blog](https://cycode.com/blog/cycode-secures-thousands-of-open-source-projects/)                            |
| [docker-slim/docker-slim](https://github.com/docker-slim/docker-slim)                           | ![](https://img.shields.io/github/stars/docker-slim/docker-slim)              | CodeSee package update                                                                                                          | [Blog](https://cycode.com/blog/cycode-secures-thousands-of-open-source-projects/)                            |
| [microsoft/fluentui](https://github.com/microsoft/fluentui)                                     | ![](https://img.shields.io/github/stars/microsoft/fluentui)                   | [2ea6195](https://github.com/microsoft/fluentui/commit/2ea6195152131766641311ee5604e746b578d8e7)                                | [Blog](https://cycode.com/blog/analyzing-the-vulnerability-that-could-have-compromised-microsoft-365-users/) |
| [tiangolo/sqlmodel](https://github.com/tiangolo/sqlmodel)                                       | ![](https://img.shields.io/github/stars/tiangolo/sqlmodel)                    | [cf36b2d](https://github.com/tiangolo/sqlmodel/commit/cf36b2d9baccf527bc61071850f102e2cd8bf6bf)                                 | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7011753940283203584/)                        |
| [tiangolo/typer](https://github.com/tiangolo/typer)                                             | ![](https://img.shields.io/github/stars/tiangolo/typer)                       | [0c106a1](https://github.com/tiangolo/typer/commit/0c106a169e5e3c7df6f98e32a6d8405c985b695a)                                    | [LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7011753940283203584/)                        |
| [autogluon/autogluon](https://github.com/autogluon/autogluon)                                   | ![](https://img.shields.io/github/stars/autogluon/autogluon)                  | [ca18fa9](https://github.com/autogluon/autogluon/commit/ca18fa9fa2071f670125fd19700cf3570a6b5119)                               |                                                                                                              |
| [liquibase/liquibase](https://github.com/liquibase/liquibase)                                   | ![](https://img.shields.io/github/stars/liquibase/liquibase)                  | [3278525](https://github.com/liquibase/liquibase/commit/3278525eaf974daea20808926f9a6816aecd01a7)                               | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |
| [ossf/scorecard](https://github.com/ossf/scorecard)                                             | ![](https://img.shields.io/github/stars/ossf/scorecard)                       | [c9f582b](https://github.com/ossf/scorecard/commit/c9f582b620a57a1a476f4e3add505ff50c51a774)                                    |                                                                                                              |
| [Ombi-app/Ombi](https://github.com/Ombi-app/Ombi)                                               | ![](https://img.shields.io/github/stars/Ombi-app/Ombi)                        | [5cc0d77](https://github.com/Ombi-app/Ombi/commit/5cc0d7727d72fe1fee8a3f6c3874d44a5b785de4)                                     | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |
| [wireapp/wire-ios](https://github.com/wireapp/wire-ios)                                         | ![](https://img.shields.io/github/stars/wireapp/wire-ios)                     | [9d39d6c](https://github.com/wireapp/wire-ios/commit/9d39d6c93b5a58a0bc8c1aba10e0d67756359630)                                  | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |
| [cloudscape-design/components](https://github.com/cloudscape-design/components)                 | ![](https://img.shields.io/github/stars/cloudscape-design/components)         | [2921d2d](https://github.com/cloudscape-design/.github/commit/2921d2d1420fef5b849d5aecbcfb9138ac6b9dcc)                         |                                                                                                              |
| [DynamoDS/Dynamo](https://github.com/DynamoDS/Dynamo)                                           | ![](https://img.shields.io/github/stars/DynamoDS/Dynamo)                      | Disabled workflow                                                                                                               | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |
| [fauna/faunadb-js](https://github.com/fauna/faunadb-js)                                         | ![](https://img.shields.io/github/stars/fauna/faunadb-js)                     | [ee6f53f](https://github.com/fauna/faunadb-js/commit/ee6f53f9c985bde41976743530e3846dee058587)                                  | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |
| [apache/incubator-kie-kogito-runtimes](https://github.com/apache/incubator-kie-kogito-runtimes) | ![](https://img.shields.io/github/stars/apache/incubator-kie-kogito-runtimes) | [53c18e5](https://github.com/apache/incubator-kie-kogito-runtimes/commit/53c18e5372e5306e0aa580f201f820b80359ad11)              | [Blog](https://cycode.com/github-actions-vulnerabilities/)                                                   |


![Raven](assets/images/raven.png)