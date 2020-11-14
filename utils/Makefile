SOURCE_DIR = ../src
TEMP_DIR = temp_work_dir
OUTPUT_DIR = ../compiled
DOC_DIR = ../docs
CUR_DIR = ${PWD}

DOC_BLACKLIST = __init__

.PHONY: all compile pycdoc copyxls

all: pycdoc compile copyxls

compile: $(OUTPUT_DIR)/gewichtung.so

pycdoc: $(OUTPUT_DIR)/dokumentation/abapys.html

copyxls: $(OUTPUT_DIR)/abapys/Materialdatenbank*.xlsx

$(OUTPUT_DIR)/gewichtung.so: $(SOURCE_DIR)/gewichtung.cpp
	g++ -std=c++11 -fPIC $^ -o $@ -shared;

$(OUTPUT_DIR)/dokumentation/abapys.html: $(SOURCE_DIR)/*.py
	mkdir -p $(TEMP_DIR)/abapys;
	cp -r $(SOURCE_DIR)/* $(TEMP_DIR)/abapys/;
	cd $(TEMP_DIR); \
	pydoc2.7 -w abapys; \
	sed -i 's:<a href=".".*</a>::' abapys.html; \
	for pyfile in $(basename $(notdir $^)); do \
	   pydoc2.7 -w abapys.$$pyfile; \
	   sed -i "s:<font color=\"#ffffff\" face=\"helvetica, arial\"><a href=\".\">index</a>.*.py</a></font>::g" abapys.$$pyfile.html; \
	done; \
	for blacklisted in $(DOC_BLACKLIST); do \
	   sed -i "s:<a href=\"abapys.$$blacklisted.html\">$$blacklisted</a><br>:<i>$$blacklisted</i><br>:" abapys.html; \
	   rm abapys.$$blacklisted.html; \
	done;
	cp $(TEMP_DIR)/*.html $(OUTPUT_DIR)/dokumentation/;
	mv $(TEMP_DIR)/*.html $(DOC_DIR)/;
	mv $(TEMP_DIR)/abapys/*.pyc $(OUTPUT_DIR)/abapys/;
	rm -r $(TEMP_DIR);

$(OUTPUT_DIR)/abapys/Materialdatenbank*.xlsx: Materialdatenbank*.xlsx
	cp $^ $@;
