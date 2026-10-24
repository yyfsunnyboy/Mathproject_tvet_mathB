"""Hand-verified PDF crop regions (PDF points, page 1-based) for the six Unit 10 BLOCKER questions.

Source: 單元10-三次函數的圖形特徵.pdf (sha256 4e9cfd42…b6).  Every region was read off the rendered page and
re-checked on the cropped image before any database write."""
PDF = "textbook_import/uploaded_sources/general/數學1/4e9cfd4278ea_單元10-三次函數的圖形特徵.pdf"
PDF_SHA256 = "4e9cfd4278ea7c7ed58386c2d91c4f48060e1df5d3757b7d8677ff2c3a0eb6e6"
# question id -> [(slot, page, bbox, description)]
REGIONS = {
    12609: [("pdf_visual_01", 3, [367, 142, 521, 388], "Γ1 red, Γ2 blue, Γ3 green curves with the black y=x^3 curve")],
    12610: [("pdf_visual_01", 5, [400, 117, 533, 338], "Γ1 red and Γ2 black curves")],
    12611: [("pdf_visual_01", 6, [379, 117, 517, 260], "Γ1 red and Γ2 black curves")],
    12621: [("pdf_visual_01", 16, [408, 412, 533, 558], "Γ1, Γ2, Γ3 curves of y=a_i x^3")],
    12626: [("pdf_visual_01", 17, [404, 408, 533, 542], "graph of the linear function y=ax+b"),
            ("pdf_visual_02", 17, [104, 487, 375, 650], "option graphs (1)-(5)")],
    12628: [("pdf_visual_01", 18, [404, 404, 529, 592], "Γ1 blue, Γ2 black, Γ3 red, Γ4 green curves of f(x)=x^3-x and translations")],
}
