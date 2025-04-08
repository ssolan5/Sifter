.PHONY: all


run:
	nix-shell --pure

clean:
	rm -rf .tmp
	rm -rf GuarddutyAlertsSampleData/


