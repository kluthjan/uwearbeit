#!/bin/bash
# ==============================================================================
# Skript: run_tests.sh
# Beschreibung: Automatisiertes Testprotokoll für Samba-Freigaben (Gruppe 3)
# Subnetz: 172.16.30.0/24 | Server-IP: 172.16.30.10
# ==============================================================================

SERVER_IP="172.16.30.10"
PASS_COUNT=0
FAIL_COUNT=0

log_test() {
    TEST_NAME=$1
    RESULT=$2
    EXPECTED=$3

    if [ "$RESULT" -eq "$EXPECTED" ]; then
        echo -e "[\e[32mPASS\e[0m] $TEST_NAME"
        ((PASS_COUNT++))
    else
        echo -e "[\e[31mFAIL\e[0m] $TEST_NAME"
        ((FAIL_COUNT++))
    fi
}

echo "=============================================================================="
echo "START DER AUTOMATISCHEN RECHTE- UND FUNKTIONSTESTS (MÜLLER & PARTNER GMBH)"
echo "=============================================================================="

# Test 1: IP-Verbindung
echo "--- TEST 1: Netzwerkkonnektivität (Ping) ---"
ping -c 2 "$SERVER_IP" &>/dev/null
log_test "Ping zu Server ($SERVER_IP)" $? 0

# Test 2: Benutzer anna
echo "--- TEST 2: Zugriffsrechte Benutzer 'anna' (Gruppe: mitarbeiter) ---"
smbclient "//$SERVER_IP/public" -U anna%Start123! -c "ls" &>/dev/null
log_test "anna -> public (Erwartet: Erfolgreich)" $? 0

smbclient "//$SERVER_IP/mitarbeiter" -U anna%Start123! -c "ls" &>/dev/null
log_test "anna -> mitarbeiter (Erwartet: Erfolgreich)" $? 0

smbclient "//$SERVER_IP/leitung" -U anna%Start123! -c "ls" &>/dev/null
if [ $? -ne 0 ]; then RESULT=0; else RESULT=1; fi
log_test "anna -> leitung (Erwartet: Verweigert)" $RESULT 0

# Test 3: Benutzer bernd
echo "--- TEST 3: Zugriffsrechte Benutzer 'bernd' (Gruppe: mitarbeiter) ---"
smbclient "//$SERVER_IP/public" -U bernd%Start123! -c "ls" &>/dev/null
log_test "bernd -> public (Erwartet: Erfolgreich)" $? 0

smbclient "//$SERVER_IP/mitarbeiter" -U bernd%Start123! -c "ls" &>/dev/null
log_test "bernd -> mitarbeiter (Erwartet: Erfolgreich)" $? 0

smbclient "//$SERVER_IP/leitung" -U bernd%Start123! -c "ls" &>/dev/null
if [ $? -ne 0 ]; then RESULT=0; else RESULT=1; fi
log_test "bernd -> leitung (Erwartet: Verweigert)" $RESULT 0

# Test 4: Benutzer chef
echo "--- TEST 4: Zugriffsrechte Benutzer 'chef' (Gruppe: leitung & mitarbeiter) ---"
smbclient "//$SERVER_IP/public" -U chef%Start123! -c "ls" &>/dev/null
log_test "chef -> public (Erwartet: Erfolgreich)" $? 0

smbclient "//$SERVER_IP/mitarbeiter" -U chef%Start123! -c "ls" &>/dev/null
log_test "chef -> mitarbeiter (Erwartet: Erfolgreich)" $? 0

smbclient "//$SERVER_IP/leitung" -U chef%Start123! -c "ls" &>/dev/null
log_test "chef -> leitung (Erwartet: Erfolgreich)" $? 0

echo "=============================================================================="
echo "TEST-ERGEBNIS ZUSAMMENFASSUNG:"
echo "Erfolgreiche Tests: $PASS_COUNT"
echo "Fehlgeschlagene Tests: $FAIL_COUNT"
echo "=============================================================================="

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "\e[32mALLE TESTS WURDEN ERFOLGREICH BESTANDEN!\e[0m"
    exit 0
else
    echo -e "\e[31mEINIGE TESTS SIND FEHLGESCHLAGEN. BITTE PRÜFE DIE KONFIGURATION.\e[0m"
    exit 1
fi
