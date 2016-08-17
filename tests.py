# L1 = ['a','b','c']
# L2 = ['1','2','3','4','5']

# res_list = [
#     {'grade': 'ok', 'rc': 0},
#     {'grade': 'warning', 'rc': 1}
# ]
#
# sub_dict = {
#     'count': 0,
#     'results': res_list
# }

answer_list = [
    {'id': '123', 'text': 'Vilnius', 'is_correct': 'True'},
    {'id': '123', 'text': 'Minsk', 'is_correct': 'False'},
    {'id': '123', 'text': 'Riga', 'is_correct': 'False'},
    {'id': '123', 'text': 'Talin', 'is_correct': 'False'},
]

question_list = [
    {'id': '321', 'text': 'What is the capital of Lithuania_1?', 'created_by': '123', 'answers': answer_list},
    {'id': '321', 'text': 'What is the capital of Lithuania_2?', 'created_by': '123', 'answers': answer_list},
    {'id': '321', 'text': 'What is the capital of Lithuania_3?', 'created_by': '123', 'answers': answer_list},
]

category_list = [
    {'id': '123', 'name': 'Biology', 'created_by': '321', 'questions': question_list},
    {'id': '123', 'name': 'History', 'created_by': '321', 'questions': question_list},
    {'id': '123', 'name': 'Maths', 'created_by': '321', 'questions': question_list}
]

my_dict = {'categories': category_list}
# for l1 in L1:
#     my_dict[l1] = {}
#
# for l1 in L1:
#     for l2 in L2:
#         my_dict[l1][l2] = question_list

print my_dict

# get a list of categories {id:xxx, name: xxx, created_by: xxx}

#get a list of questions for each category {id:xxx, text: xxx, created_by: xxx}

#get a list of answers for each question {id:xxx, text: xxx, is_correct: xxx, created_by: xxx}