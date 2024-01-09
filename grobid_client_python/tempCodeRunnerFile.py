    client = GrobidClient(config_path="./config.json")
    client.process("processFulltextDocument", "./tests/test_pdf", output="./tests/test_out/", consolidate_citations=False, tei_coordinates=True, force=False)
