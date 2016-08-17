// TODO remove the js file, decided to use a different approach

//$(document).ready(function() {
//
//        this.catListElem = document.getElementById('categories-select');
//        this.catListElem.innerHTML = '';
//
//        for (el in cat) {
//            elem = document.createElement('option');
//            elem.textContent = el;
//            elem.value = cat[el];
//
//            elem.addEventListener('click', (function(catCopy) {
//                    return function() {
//                        alert('Category clicked: ' + catCopy);
//                        $.getJSON($SCRIPT_ROOT + '/_category2python', {
//                            category_id: JSON.stringify(catCopy)
//                            }, function(data){
//                                console.log(data.result)
//                                $( "#result" ).text(data.result);
//                            });
//                    };
//                })(cat[el]));
//
//            this.catListElem.appendChild(elem)
//        }
//
//});
