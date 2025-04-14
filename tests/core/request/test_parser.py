"""
解析器測試模組

測試各種響應解析器的功能，包括：
1. JSON 解析器
2. XML 解析器
3. HTML 解析器
4. 文本解析器
5. 二進制解析器
"""

import pytest
import json
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from selenium_base.core.request.parser import (
    RequestParser,
    ResponseParser,
    HTMLParser,
    JSONParser,
    XMLParser,
    TextParser,
    BinaryParser,
    PDFParser,
    ExcelParser,
    CSVParser,
    ImageParser,
    VideoParser,
    AudioParser,
    DocumentParser,
    ArchiveParser,
    CustomParser,
    ParserFactory,
    ParserRegistry,
    ParserError,
    ParserNotFoundError,
    ParserValidationError,
    ParserConfigurationError,
    ParserExecutionError,
    ParserTimeoutError,
    ParserConnectionError,
    ParserAuthenticationError,
    ParserAuthorizationError,
    ParserRateLimitError,
    ParserQuotaExceededError,
    ParserServiceUnavailableError,
    ParserMaintenanceError,
    ParserDeprecatedError,
    ParserVersionError,
    ParserCompatibilityError,
    ParserDependencyError,
    ParserResourceError,
    ParserStateError,
    ParserContextError,
    ParserEnvironmentError,
    ParserSystemError,
    ParserRuntimeError,
    ParserLogicError,
    ParserSyntaxError,
    ParserSemanticError,
    ParserTypeError,
    ParserValueError,
    ParserAttributeError,
    ParserKeyError,
    ParserIndexError,
    ParserNameError,
    ParserImportError,
    ParserModuleNotFoundError,
    ParserPackageNotFoundError,
    ParserClassNotFoundError,
    ParserFunctionNotFoundError,
    ParserVariableNotFoundError,
    ParserConstantNotFoundError,
    ParserEnumNotFoundError,
    ParserStructNotFoundError,
    ParserUnionNotFoundError,
    ParserInterfaceNotFoundError,
    ParserTraitNotFoundError,
    ParserProtocolNotFoundError,
    ParserAbstractNotFoundError,
    ParserConcreteNotFoundError,
    ParserFinalNotFoundError,
    ParserStaticNotFoundError,
    ParserInstanceNotFoundError,
    ParserObjectNotFoundError,
    ParserMethodNotFoundError,
    ParserPropertyNotFoundError,
    ParserFieldNotFoundError,
    ParserParameterNotFoundError,
    ParserArgumentNotFoundError,
    ParserReturnNotFoundError,
    ParserYieldNotFoundError,
    ParserAwaitNotFoundError,
    ParserAsyncNotFoundError,
    ParserGeneratorNotFoundError,
    ParserIteratorNotFoundError,
    ParserIterableNotFoundError,
    ParserSequenceNotFoundError,
    ParserMappingNotFoundError,
    ParserSetNotFoundError,
    ParserFrozenSetNotFoundError,
    ParserDictNotFoundError,
    ParserListNotFoundError,
    ParserTupleNotFoundError,
    ParserRangeNotFoundError,
    ParserSliceNotFoundError,
    ParserBytesNotFoundError,
    ParserByteArrayNotFoundError,
    ParserMemoryViewNotFoundError,
    ParserStrNotFoundError,
    ParserIntNotFoundError,
    ParserFloatNotFoundError,
    ParserComplexNotFoundError,
    ParserBoolNotFoundError,
    ParserNoneNotFoundError,
    ParserEllipsisNotFoundError,
    ParserNotImplementedNotFoundError,
    ParserBaseExceptionNotFoundError,
    ParserExceptionNotFoundError,
    ParserArithmeticErrorNotFoundError,
    ParserAssertionErrorNotFoundError,
    ParserAttributeErrorNotFoundError,
    ParserBufferErrorNotFoundError,
    ParserBytesWarningNotFoundError,
    ParserDeprecationWarningNotFoundError,
    ParserEOFErrorNotFoundError,
    ParserEnvironmentErrorNotFoundError,
    ParserFloatingPointErrorNotFoundError,
    ParserFutureWarningNotFoundError,
    ParserGeneratorExitNotFoundError,
    ParserImportErrorNotFoundError,
    ParserImportWarningNotFoundError,
    ParserIndentationErrorNotFoundError,
    ParserIndexErrorNotFoundError,
    ParserKeyErrorNotFoundError,
    ParserKeyboardInterruptNotFoundError,
    ParserLookupErrorNotFoundError,
    ParserMemoryErrorNotFoundError,
    ParserNameErrorNotFoundError,
    ParserNotImplementedErrorNotFoundError,
    ParserOSErrorNotFoundError,
    ParserOverflowErrorNotFoundError,
    ParserPendingDeprecationWarningNotFoundError,
    ParserRecursionErrorNotFoundError,
    ParserReferenceErrorNotFoundError,
    ParserResourceWarningNotFoundError,
    ParserRuntimeErrorNotFoundError,
    ParserRuntimeWarningNotFoundError,
    ParserStopIterationNotFoundError,
    ParserSyntaxErrorNotFoundError,
    ParserSyntaxWarningNotFoundError,
    ParserSystemErrorNotFoundError,
    ParserSystemExitNotFoundError,
    ParserTabErrorNotFoundError,
    ParserTypeErrorNotFoundError,
    ParserUnboundLocalErrorNotFoundError,
    ParserUnicodeDecodeErrorNotFoundError,
    ParserUnicodeEncodeErrorNotFoundError,
    ParserUnicodeErrorNotFoundError,
    ParserUnicodeTranslateErrorNotFoundError,
    ParserUnicodeWarningNotFoundError,
    ParserUserWarningNotFoundError,
    ParserValueErrorNotFoundError,
    ParserWarningNotFoundError,
    ParserZeroDivisionErrorNotFoundError,
)
from selenium_base.utils.exceptions import RequestError

@pytest.fixture
def base_config():
    """基本配置"""
    return {
        'test_key': 'test_value'
    }

@pytest.fixture
def mock_response():
    """模擬響應對象"""
    response = MagicMock()
    response.text = 'test response'
    response.content = b'test content'
    return response

@pytest.fixture
def json_response(mock_response):
    """JSON 響應"""
    mock_response.json.return_value = {'key': 'value'}
    return mock_response

@pytest.fixture
def xml_response(mock_response):
    """XML 響應"""
    mock_response.text = '<root><item>value</item></root>'
    return mock_response

@pytest.fixture
def html_response(mock_response):
    """HTML 響應"""
    mock_response.text = '<html><body><div class="test">content</div></body></html>'
    return mock_response

def test_base_parser(base_config):
    """測試基類解析器"""
    parser = ResponseParser(base_config)
    assert parser.config == base_config
    
    # 基類方法應該拋出 NotImplementedError
    with pytest.raises(NotImplementedError):
        parser.parse(MagicMock())

def test_json_parser(base_config, json_response):
    """測試 JSON 解析器"""
    parser = JSONParser(base_config)
    result = parser.parse(json_response)
    
    assert result == {'key': 'value'}
    json_response.json.assert_called_once()

def test_json_parser_error(base_config, mock_response):
    """測試 JSON 解析錯誤"""
    parser = JSONParser(base_config)
    mock_response.json.side_effect = Exception('JSON error')
    
    with pytest.raises(ParserError) as exc_info:
        parser.parse(mock_response)
    
    assert 'JSON 解析錯誤' in str(exc_info.value)

def test_xml_parser(base_config, xml_response):
    """測試 XML 解析器"""
    parser = XMLParser(base_config)
    result = parser.parse(xml_response)
    
    assert isinstance(result, ET.Element)
    assert result.tag == 'root'
    assert result.find('item').text == 'value'

def test_xml_parser_error(base_config, mock_response):
    """測試 XML 解析錯誤"""
    parser = XMLParser(base_config)
    mock_response.text = 'invalid xml'
    
    with pytest.raises(ParserError) as exc_info:
        parser.parse(mock_response)
    
    assert 'XML 解析錯誤' in str(exc_info.value)

def test_xml_find_element(base_config, xml_response):
    """測試 XML 元素查找"""
    parser = XMLParser(base_config)
    xml = parser.parse(xml_response)
    
    element = parser.find_element(xml, 'item')
    assert element is not None
    assert element.text == 'value'
    
    element = parser.find_element(xml, 'nonexistent')
    assert element is None

def test_xml_find_elements(base_config, xml_response):
    """測試 XML 多元素查找"""
    parser = XMLParser(base_config)
    xml = parser.parse(xml_response)
    
    elements = parser.find_elements(xml, 'item')
    assert len(elements) == 1
    assert elements[0].text == 'value'
    
    elements = parser.find_elements(xml, 'nonexistent')
    assert len(elements) == 0

def test_html_parser(base_config, html_response):
    """測試 HTML 解析器"""
    parser = HTMLParser(base_config)
    result = parser.parse(html_response)
    
    assert isinstance(result, BeautifulSoup)
    assert result.find('div', class_='test').text == 'content'

def test_html_parser_custom_config(base_config, html_response):
    """測試 HTML 解析器自定義配置"""
    config = {
        **base_config,
        'parser': 'lxml',
        'encoding': 'utf-8'
    }
    parser = HTMLParser(config)
    result = parser.parse(html_response)
    
    assert isinstance(result, BeautifulSoup)
    assert result.original_encoding == 'utf-8'

def test_html_parser_error(base_config, mock_response):
    """測試 HTML 解析錯誤"""
    parser = HTMLParser(base_config)
    mock_response.text = '<invalid>html'
    
    with pytest.raises(ParserError) as exc_info:
        parser.parse(mock_response)
    
    assert 'HTML 解析錯誤' in str(exc_info.value)

def test_html_find_element(base_config, html_response):
    """測試 HTML 元素查找"""
    parser = HTMLParser(base_config)
    html = parser.parse(html_response)
    
    element = parser.find_element(html, '.test')
    assert element is not None
    assert element.text == 'content'
    
    element = parser.find_element(html, '.nonexistent')
    assert element is None

def test_html_find_elements(base_config, html_response):
    """測試 HTML 多元素查找"""
    parser = HTMLParser(base_config)
    html = parser.parse(html_response)
    
    elements = parser.find_elements(html, '.test')
    assert len(elements) == 1
    assert elements[0].text == 'content'
    
    elements = parser.find_elements(html, '.nonexistent')
    assert len(elements) == 0

def test_text_parser(base_config, mock_response):
    """測試文本解析器"""
    parser = TextParser(base_config)
    result = parser.parse(mock_response)
    
    assert result == 'test response'

def test_text_parser_error(base_config, mock_response):
    """測試文本解析錯誤"""
    parser = TextParser(base_config)
    mock_response.text = None
    
    with pytest.raises(ParserError) as exc_info:
        parser.parse(mock_response)
    
    assert '文本解析錯誤' in str(exc_info.value)

def test_binary_parser(base_config, mock_response):
    """測試二進制解析器"""
    parser = BinaryParser(base_config)
    result = parser.parse(mock_response)
    
    assert result == b'test content'

def test_binary_parser_error(base_config, mock_response):
    """測試二進制解析錯誤"""
    parser = BinaryParser(base_config)
    mock_response.content = None
    
    with pytest.raises(ParserError) as exc_info:
        parser.parse(mock_response)
    
    assert '二進制數據解析錯誤' in str(exc_info.value)

def test_parser_factory(base_config):
    """測試解析器工廠"""
    # 測試支持的解析器類型
    assert isinstance(ParserFactory.create('json', base_config), JSONParser)
    assert isinstance(ParserFactory.create('xml', base_config), XMLParser)
    assert isinstance(ParserFactory.create('html', base_config), HTMLParser)
    assert isinstance(ParserFactory.create('text', base_config), TextParser)
    assert isinstance(ParserFactory.create('binary', base_config), BinaryParser)
    
    # 測試不支持的解析器類型
    with pytest.raises(ParserError) as exc_info:
        ParserFactory.create('unsupported', base_config)
    
    assert '不支持的解析器類型' in str(exc_info.value) 