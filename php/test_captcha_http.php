<?php
/*
Licencováno pod MIT Licencí

© 2008 Seznam.cz, a.s.

Tímto se uděluje bezúplatná nevýhradní licence k oprávnění užívat Software,
časově i místně neomezená, v souladu s příslušnými ustanoveními autorského zákona.

Nabyvatel/uživatel, který obdržel kopii tohoto softwaru a další přidružené
soubory (dále jen „software“) je oprávněn k nakládání se softwarem bez
jakýchkoli omezení, včetně bez omezení práva software užívat, pořizovat si
z něj kopie, měnit, sloučit, šířit, poskytovat zcela nebo zčásti třetí osobě
(podlicence) či prodávat jeho kopie, za následujících podmínek:

- výše uvedené licenční ujednání musí být uvedeno na všech kopiích nebo
podstatných součástech Softwaru.

- software je poskytován tak jak stojí a leží, tzn. autor neodpovídá
za jeho vady, jakož i možné následky, ledaže věc nemá vlastnost, o níž autor
prohlásí, že ji má, nebo kterou si nabyvatel/uživatel výslovně vymínil.



Licenced under the MIT License

Copyright (c) 2008 Seznam.cz, a.s.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


DESCRIPTION
Test captchi xmlrpc

AUTHOR
Josef Kyrian <josef.kyrian@firma.seznam.cz>

*/


require_once 'captcha.class.php';
require_once 'captcha_http.class.php';

// vytvorit objekt
$captcha = new CaptchaHTTP("captcha.seznam.cz", 80);
// nastavit pripadne proxy
//$captcha->setProxy("proxy", 3128);


// pokud zadna akce neni definovana
if (!isset($_REQUEST['action'])) {
	// vytvorit novou captchu
	try {
		$hash = $captcha->create();
	}catch (Exception $e) {
		echo '<p><b>Nepodarilo se vytvorit captchu</b></p>';
		echo '<pre>'.$e->__toString().'</pre>';
		exit;
	}

	?>
	<form action="<?php echo $_SERVER["SCRIPT_NAME"];?>" method="post">
		<input type="hidden" name="action" value="check">
		<input type="hidden" name="hash" value="<?php echo $hash;?>">

		Opiste kod:<br>
		<img src="<?php echo $captcha->getImage($hash);?>">
		<br>
		<label for="code">Kod:</label>
		<input type="text" id="code" name="code" size="5" maxlength="5">
		<input type="submit" value="Zkontrolovat">
	</form>
	<?php

// pokud se zkontrolovat kod na pro dany hash
}else if ($_REQUEST['action'] == 'check') {
	// vytvorit novou captchu
	try {
		$ok = $captcha->check($_REQUEST['hash'], $_REQUEST['code']);
	}catch (Exception $e) {
		echo '<p><b>Nepodarilo se overit captchu</b></p>';
		echo '<pre>'.$e->__toString().'</pre>';
		exit;
	}

	if ($ok) {
		echo '<b>OK</b>';
	}else {
		echo '<b>Kod se neshoduje</b>';
	}
	echo '<br><a href="'.$_SERVER["SCRIPT_NAME"].'">Zpet</a>';
}
?>
