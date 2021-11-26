def getitem_by_list(obj, l):
	return [obj[i] for i in l]

def etex(s: str):
	result = ''
	for c in s:
		if c == '\\':  result += '\\textbackslash '
		elif c == '~': result += '\\textasciitilde '
		elif c == '{': result += '\\{'
		elif c == '}': result += '\\}'
		elif c == '&': result += '\\&'
		elif c == ' ': result += '~'
		else: result += c
	return result

filters = {
	'getitem_by_list': getitem_by_list,
	'etex': etex
}