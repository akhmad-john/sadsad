

def draw_frame_border(workbook, worksheet, first_row, first_col, rows_count, cols_count, width=1):

    # top left corner
    worksheet.conditional_format(first_row, first_col,
                                 first_row, first_col,
                                 {'type': 'formula', 'criteria': 'True',
                                  'format': workbook.add_format({'top': width, 'left': width})})
    # top right corner
    worksheet.conditional_format(first_row, first_col + cols_count - 1,
                                 first_row, first_col + cols_count - 1,
                                 {'type': 'formula', 'criteria': 'True',
                                  'format': workbook.add_format({'top': width, 'right': width})})
    # bottom left corner
    worksheet.conditional_format(first_row + rows_count - 1, first_col,
                                 first_row + rows_count - 1, first_col,
                                 {'type': 'formula', 'criteria': 'True',
                                  'format': workbook.add_format({'bottom': width, 'left': width})})
    # bottom right corner
    worksheet.conditional_format(first_row + rows_count - 1, first_col + cols_count - 1,
                                 first_row + rows_count - 1, first_col + cols_count - 1,
                                 {'type': 'formula', 'criteria': 'True',
                                  'format': workbook.add_format({'bottom': width, 'right': width})})

    # top
    worksheet.conditional_format(first_row, first_col + 1,
                                 first_row, first_col + cols_count - 2,
                                 {'type': 'formula', 'criteria': 'True', 'format': workbook.add_format({'top': width})})
    # left
    worksheet.conditional_format(first_row + 1,              first_col,
                                 first_row + rows_count - 2, first_col,
                                 {'type': 'formula', 'criteria': 'True', 'format': workbook.add_format({'left': width})})
    # bottom
    worksheet.conditional_format(first_row + rows_count - 1, first_col + 1,
                                 first_row + rows_count - 1, first_col + cols_count - 2,
                                 {'type': 'formula', 'criteria': 'True', 'format': workbook.add_format({'bottom': width})})
    # right
    worksheet.conditional_format(first_row + 1,              first_col + cols_count - 1,
                                 first_row + rows_count - 2, first_col + cols_count - 1,
                                 {'type': 'formula', 'criteria': 'True', 'format': workbook.add_format({'right': width})})
