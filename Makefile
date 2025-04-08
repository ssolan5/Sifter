.PHONY: all


run:
	nix-shell --pure

clean:
	rm -rf .tmp
	rm -rf GuarddutyAlertsSampleData/
	rm -rf GuarddutyAlertsSampleData-1/



