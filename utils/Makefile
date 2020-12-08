SOURCE_DIR = ../abapys
TEMP_DIR = temp_work_dir
LIB_DIR = ../
DOC_DIR = ../docs

DOC_BLACKLIST = __init__

.PHONY: all compile pycdoc 

pycdoc: $(DOC_DIR)/abapys.html

all: pycdoc compile

compile: $(LIB_DIR)/gewichtung.so

$(LIB_DIR)/gewichtung.so: $(LIB_DIR)/gewichtung.cpp
	g++ -std=c++11 -fPIC $^ -o $@ -shared;

$(DOC_DIR)/abapys.html: $(SOURCE_DIR)/*.py
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
	mv $(TEMP_DIR)/*.html $(DOC_DIR)/;
	rm -r $(TEMP_DIR);
