import React from 'react';
import ReactDOM from 'react-dom';
import QueryInput from './components/QueryInput';
import TreeRenderer from './components/TreeRenderer';




var onProcessed = function(response) {
    ReactDOM.render(
        <TreeRenderer tree={response}/>,
        document.getElementById('root')
      );
}

ReactDOM.render(
  <TreeRenderer tree={response}/>,
    document.getElementById('root')
  );
  
